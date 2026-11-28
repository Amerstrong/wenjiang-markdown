export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // ── CORS preflight ──
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Key',
        }
      });
    }

    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    };

    // ────────────────────────────────────────
    // Alipay PC Website Payment (alipay.trade.page.pay)
    // 1. POST /api/pay/create
    // 2. POST /api/pay/ali-notify
    // 3. GET  /api/pay/status?order_no=xxx
    // ────────────────────────────────────────
    if (url.pathname === '/api/pay/create' && request.method === 'POST') {
      try {
        if (!env.DB) {
          return new Response(JSON.stringify({ ok: false, message: 'D1 数据库未绑定' }), { status: 500, headers });
        }
        if (!env.ALI_APP_ID || !env.ALI_PRIVATE_KEY) {
          return new Response(JSON.stringify({ ok: false, message: '支付宝商户配置缺失' }), { status: 500, headers });
        }

        const body = await request.json();
        const productId = String(body.product_id || '').trim();
        const email = String(body.email || '').trim().slice(0, 120);
        const product = PAY_PRODUCTS[productId];

        if (!product) {
          return new Response(JSON.stringify({ ok: false, message: '无效的商品 ID' }), { status: 400, headers });
        }

        const outTradeNo = generateOutTradeNo();
        const { timestamp } = getBeijingTimeParts();
        const createdAt = new Date().toISOString();

        await env.DB.prepare(
          'INSERT INTO orders (out_trade_no, product_id, amount, email, status, created_at) VALUES (?, ?, ?, ?, ?, ?)'
        )
          .bind(outTradeNo, productId, Number(product.amount), email, 'PENDING', createdAt)
          .run();

        const aliParams = {
          app_id: env.ALI_APP_ID,
          method: 'alipay.trade.page.pay',
          format: 'JSON',
          charset: 'utf-8',
          sign_type: 'RSA2',
          timestamp,
          version: '1.0',
          notify_url: 'https://wojingfang.cn/api/pay/ali-notify',
          return_url: `https://wojingfang.cn/tools/filebeam.html?order_no=${encodeURIComponent(outTradeNo)}`,
          biz_content: JSON.stringify({
            out_trade_no: outTradeNo,
            product_code: 'FAST_INSTANT_TRADE_PAY',
            total_amount: product.amount,
            subject: product.subject,
          }),
        };

        const signContent = buildAlipaySignContent(aliParams, ['sign']);
        const sign = await signAlipayRSA2(signContent, env.ALI_PRIVATE_KEY);
        const query = new URLSearchParams({ ...aliParams, sign });
        const payUrl = `https://openapi.alipay.com/gateway.do?${query.toString()}`;

        return new Response(JSON.stringify({
          ok: true,
          order_no: outTradeNo,
          pay_url: payUrl,
        }), { headers });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, message: '创建订单失败: ' + e.message }), {
          status: 500,
          headers,
        });
      }
    }

    if (url.pathname === '/api/pay/ali-notify' && request.method === 'POST') {
      const textHeaders = { 'Content-Type': 'text/plain; charset=utf-8' };
      try {
        if (!env.DB || !env.ALI_PUBLIC_KEY || !env.ALI_APP_ID || !env.FILEBEAM_SECRET_KEY) {
          return new Response('failure', { status: 500, headers: textHeaders });
        }

        const rawBody = await request.text();
        const formParams = new URLSearchParams(rawBody);
        const paramsObj = {};
        for (const [k, v] of formParams.entries()) {
          paramsObj[k] = v;
        }

        const sign = paramsObj.sign || '';
        const verifyContent = buildAlipaySignContent(paramsObj, ['sign', 'sign_type']);
        const isValidSig = await verifyAlipayRSA2(verifyContent, sign, env.ALI_PUBLIC_KEY);
        if (!isValidSig) {
          return new Response('failure', { status: 400, headers: textHeaders });
        }

        if (paramsObj.app_id !== env.ALI_APP_ID) {
          return new Response('failure', { status: 400, headers: textHeaders });
        }

        if (paramsObj.trade_status !== 'TRADE_SUCCESS' && paramsObj.trade_status !== 'TRADE_FINISHED') {
          return new Response('success', { status: 200, headers: textHeaders });
        }

        const outTradeNo = paramsObj.out_trade_no;
        if (!outTradeNo) {
          return new Response('failure', { status: 400, headers: textHeaders });
        }

        const order = await env.DB.prepare(
          'SELECT out_trade_no, product_id, amount, status, license_key FROM orders WHERE out_trade_no = ?'
        )
          .bind(outTradeNo)
          .first();

        if (!order) {
          return new Response('failure', { status: 404, headers: textHeaders });
        }

        const expectedAmount = Number(order.amount).toFixed(2);
        const actualAmount = Number(paramsObj.total_amount).toFixed(2);
        if (expectedAmount !== actualAmount) {
          return new Response('failure', { status: 400, headers: textHeaders });
        }

        // 幂等处理：已是 PAID 直接返回 success
        if (order.status === 'PAID') {
          return new Response('success', { status: 200, headers: textHeaders });
        }

        if (order.status === 'PENDING') {
          const licenseKey = await generateFileBeamCode(env.FILEBEAM_SECRET_KEY);
          const tradeNo = paramsObj.trade_no || '';
          const paidAt = new Date().toISOString();

          await env.DB.prepare(
            'UPDATE orders SET status = ?, license_key = ?, trade_no = ?, paid_at = ? WHERE out_trade_no = ? AND status = ?'
          )
            .bind('PAID', licenseKey, tradeNo, paidAt, outTradeNo, 'PENDING')
            .run();

          await sendFeishu(
            env,
            `💰【支付宝自动成单】\n订单号: ${outTradeNo}\n商品: ${order.product_id}\n金额: ¥${expectedAmount}\n激活码: ${licenseKey}\n支付宝流水: ${tradeNo}`
          );
        }

        return new Response('success', { status: 200, headers: textHeaders });
      } catch (e) {
        return new Response('failure', { status: 500, headers: textHeaders });
      }
    }

    if (url.pathname === '/api/pay/status' && request.method === 'GET') {
      try {
        if (!env.DB) {
          return new Response(JSON.stringify({ ok: false, message: 'D1 数据库未绑定' }), { status: 500, headers });
        }
        const orderNo = String(url.searchParams.get('order_no') || '').trim();
        if (!orderNo) {
          return new Response(JSON.stringify({ ok: false, message: '缺少 order_no 参数' }), { status: 400, headers });
        }

        const order = await env.DB.prepare(
          'SELECT status, product_id, license_key FROM orders WHERE out_trade_no = ?'
        )
          .bind(orderNo)
          .first();

        if (!order) {
          return new Response(JSON.stringify({ status: 'NOT_FOUND', product_id: null, license_key: null }), {
            status: 404,
            headers,
          });
        }

        return new Response(JSON.stringify({
          status: order.status,
          product_id: order.product_id,
          license_key: order.status === 'PAID' ? order.license_key : null,
        }), { headers });
      } catch (e) {
        return new Response(JSON.stringify({ ok: false, message: '查询订单失败: ' + e.message }), {
          status: 500,
          headers,
        });
      }
    }

    // ────────────────────────────────────────
    // FileBeam stateless activation-code verification
    // POST /api/activate { activation_code }
    // Format: FB-<8 payload chars>-<8 HMAC-SHA256 chars>
    // Zero ACTIVATION_KV reads or writes.
    // ────────────────────────────────────────
    if (url.pathname === '/api/activate' && request.method === 'POST') {
      let activationCode = '';
      try {
        const payload = await request.json();
        activationCode = String(payload.activation_code || '').trim().toUpperCase();
      } catch {
        return new Response(JSON.stringify({ valid: false, message: '请求格式错误' }), {
          status: 400,
          headers,
        });
      }

      if (!activationCode) {
        return new Response(JSON.stringify({ valid: false, message: '激活码不能为空' }), {
          status: 400,
          headers,
        });
      }

      if (!activationCode.startsWith('FB-')) {
        const raw = await env.ACTIVATION_KV.get(activationCode);
        if (!raw) {
          return new Response(JSON.stringify({ valid: false, message: '激活码不存在' }), {
            headers,
          });
        }
        try {
          const legacy = JSON.parse(raw);
          const validLegacy =
            legacy.status === 'done'
            || legacy.activationCode === activationCode
            || legacy.code === activationCode
            || legacy.type === 'license';
          return new Response(JSON.stringify({
            valid: validLegacy,
            product: validLegacy ? (legacy.product || 'Wenjiang_Markdown_Office') : null,
            message: validLegacy ? '激活码验证成功' : '激活码状态无效',
          }), { headers });
        } catch {
          return new Response(JSON.stringify({ valid: false, message: '授权数据异常' }), {
            headers,
          });
        }
      }

      const parts = activationCode.split('-');
      if (
        !env.FILEBEAM_SECRET_KEY
        || parts.length !== 3
        || parts[0] !== 'FB'
        || parts[1].length !== 8
        || parts[2].length !== 8
      ) {
        return new Response(JSON.stringify({ valid: false, message: '激活码格式不正确' }), {
          headers,
        });
      }

      const key = await crypto.subtle.importKey(
        'raw',
        new TextEncoder().encode(env.FILEBEAM_SECRET_KEY),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign'],
      );
      const signature = await crypto.subtle.sign(
        'HMAC',
        key,
        new TextEncoder().encode(`FB-${parts[1]}`),
      );
      const expected = Array.from(new Uint8Array(signature))
        .map((byte) => byte.toString(16).padStart(2, '0'))
        .join('')
        .slice(0, 8)
        .toUpperCase();

      if (parts[2] !== expected) {
        return new Response(JSON.stringify({ valid: false, message: '激活码签名无效' }), {
          headers,
        });
      }

      return new Response(JSON.stringify({
        valid: true,
        product: 'FileBeam_Pro',
        message: '激活码验证成功',
      }), {
        headers,
      });
    }

    // ────────────────────────────────────────
    // 1. 用户提交机器码（付款后点按钮触发）
    // ────────────────────────────────────────
    if (url.pathname === '/submit' && request.method === 'POST') {
      try {
        let { machineCode } = await request.json();
        if (machineCode) machineCode = machineCode.toUpperCase();

        if (!machineCode) {
          return new Response(JSON.stringify({ success: false, msg: '机器码不能为空' }), { headers });
        }

        // 检查是否已经提交过
        const existing = await env.ACTIVATION_KV.get(machineCode);
        if (existing) {
          const data = JSON.parse(existing);
          if (data.status === 'done') {
            return new Response(JSON.stringify({ success: true, status: 'done', activation: data.activationCode }), { headers });
          }
          // 已存在但未完成，重新发飞书通知
          const retryText = `通知：新激活订单提醒！用户正在等待...\n机器码: ${machineCode}\n状态: 持续待确认\n\n核实收款后请在卖家后台激活`;
          await sendFeishu(env, retryText);
          return new Response(JSON.stringify({ success: true, status: data.status, msg: '订单已提交，请耐心等待' }), { headers });
        }

        // 新订单写入
        const orderData = {
          machineCode,
          status: 'pending',
          channel: 'website',
          submitTime: new Date().toISOString(),
          activationCode: null,
          note: null
        };
        await env.ACTIVATION_KV.put(machineCode, JSON.stringify(orderData));

        // 飞书通知
        const notifyText = `🌐【网站新订单】\n机器码: ${machineCode}\n状态: 待确认\n\n请核实收款后在卖家后台激活`;
        await sendFeishu(env, notifyText);

        return new Response(JSON.stringify({ success: true, status: 'pending', msg: '提交成功，确认付款后稍作等待即可完成激活' }), { headers });
      } catch (e) {
        return new Response(JSON.stringify({ success: false, msg: '提交格式错误' }), { status: 400, headers });
      }
    }

    // ────────────────────────────────────────
    // 2. 用户查询状态（网页/软件内轮询）
    // ────────────────────────────────────────
    if (url.pathname === '/query') {
      let machineCode = url.searchParams.get('code');
      if (machineCode) machineCode = machineCode.toUpperCase();
      if (!machineCode) {
        return new Response(JSON.stringify({ success: false, msg: '缺少code参数' }), { headers });
      }

      // 采集来源信息
      const srcInfo = getSourceInfo(request, url);

      const raw = await env.ACTIVATION_KV.get(machineCode);
      if (!raw) {
        // 首次查询自动创建订单
        const orderData = {
          machineCode,
          status: 'pending',
          channel: srcInfo.channel,
          submitTime: new Date().toISOString(),
          activationCode: null,
          note: null,
          // 来源追踪字段
          _ip: srcInfo.ip,
          _referer: srcInfo.referer,
          _ua: srcInfo.ua,
          _uaShort: srcInfo.uaShort,
        };
        await env.ACTIVATION_KV.put(machineCode, JSON.stringify(orderData));

        const notifyText = `🚨【新查询订单】\n机器码: ${machineCode}\n来源: ${srcInfo.channel}\n页面: ${srcInfo.referer || '未知'}\nIP: ${srcInfo.ip}\n设备: ${srcInfo.uaShort}\n\n请核实用户是否已付款，确认后在卖家后台激活`;
        await sendFeishu(env, notifyText);

        return new Response(JSON.stringify({ success: false, msg: '订单已创建，等待审核' }), { headers });
      }

      // 已存在的订单：追加更新来源（如首次记录不完整）
      const data = JSON.parse(raw);
      if (!data._ip && srcInfo.ip) {
        data._ip = srcInfo.ip;
        data._referer = data._referer || srcInfo.referer;
        data._ua = data._ua || srcInfo.ua;
        data._uaShort = data._uaShort || srcInfo.uaShort;
        await env.ACTIVATION_KV.put(machineCode, JSON.stringify(data));
      }

      if (data.status === 'done' && data.activationCode) {
        return new Response(JSON.stringify({ success: true, status: 'done', activation: data.activationCode }), { headers });
      }
      return new Response(JSON.stringify({ success: false, status: data.status, msg: '正在处理中，请稍候' }), { headers });
    }

    // ────────────────────────────────────────
    // 3. 卖家激活接口（旧版，兼容树莓派/外部调用）
    //    POST /activate  Header: X-Auth-Key
    // ────────────────────────────────────────
    if (url.pathname === '/activate' && request.method === 'POST') {
      const authKey = request.headers.get('X-Auth-Key');
      if (authKey !== env.ADMIN_KEY) {
        return new Response(JSON.stringify({ success: false, msg: '无权限' }), { status: 403, headers });
      }

      try {
        let { machineCode, activationCode } = await request.json();
        if (machineCode) machineCode = machineCode.toUpperCase();
        if (!machineCode || !activationCode) {
          return new Response(JSON.stringify({ success: false, msg: '参数不完整' }), { status: 400, headers });
        }

        const raw = await env.ACTIVATION_KV.get(machineCode);
        let data = raw ? JSON.parse(raw) : { machineCode, submitTime: new Date().toISOString(), channel: 'manual', note: null };
        data.status = 'done';
        data.activationCode = activationCode;
        data.activateTime = new Date().toISOString();
        await env.ACTIVATION_KV.put(machineCode, JSON.stringify(data));

        return new Response(JSON.stringify({ success: true, msg: '激活码写入成功' }), { headers });
      } catch (e) {
        return new Response(JSON.stringify({ success: false, msg: '请求格式错误' }), { status: 400, headers });
      }
    }

    // ────────────────────────────────────────
    // 4. 获取待处理订单（兼容旧版树莓派拉取）
    // ────────────────────────────────────────
    if (url.pathname === '/pending' && request.method === 'GET') {
      const authKey = request.headers.get('X-Auth-Key');
      if (authKey !== env.ADMIN_KEY) return new Response('Unauthorized', { status: 403 });

      try {
        const orders = await getAllOrders(env);
        const pending = orders.filter(o => o.status === 'pending').map(o => o.machineCode);
        return new Response(JSON.stringify(pending), { headers });
      } catch (e) {
        return new Response(JSON.stringify([]), { headers });
      }
    }

    // ════════════════════════════════════════
    // 新增：卖家后台 Admin API
    // ════════════════════════════════════════

    // ────────────────────────────────────────
    // 5. 卖家一键激活（HMAC自动算号）
    //    POST /admin/activate  Header: X-Auth-Key
    //    Body: { machineCode, note? }
    // ────────────────────────────────────────
    if (url.pathname === '/admin/activate' && request.method === 'POST') {
      const authKey = request.headers.get('X-Auth-Key');
      if (authKey !== env.ADMIN_KEY) {
        return new Response(JSON.stringify({ success: false, msg: '密码错误，无权限' }), { status: 403, headers });
      }

      try {
        let { machineCode, note } = await request.json();
        if (machineCode) machineCode = machineCode.trim().toUpperCase();
        if (!machineCode) {
          return new Response(JSON.stringify({ success: false, msg: '机器码不能为空' }), { status: 400, headers });
        }

        // 用 HMAC-SHA256 确定性生成激活码
        const activationCode = await generateActivationCode(machineCode, env.HMAC_SECRET || env.ADMIN_KEY);

        // 写入/更新 KV
        const raw = await env.ACTIVATION_KV.get(machineCode);
        let data = raw ? JSON.parse(raw) : {
          machineCode,
          submitTime: new Date().toISOString(),
          channel: 'xianyu',
        };
        data.status = 'done';
        data.activationCode = activationCode;
        data.activateTime = new Date().toISOString();
        data.note = note || data.note || null;
        await env.ACTIVATION_KV.put(machineCode, JSON.stringify(data));

        return new Response(JSON.stringify({
          success: true,
          activationCode,
          machineCode,
          msg: '激活成功'
        }), { headers });
      } catch (e) {
        return new Response(JSON.stringify({ success: false, msg: '请求格式错误: ' + e.message }), { status: 400, headers });
      }
    }

    // ────────────────────────────────────────
    // 6. 查询所有激活记录（卖家后台列表）
    //    GET /admin/orders  Header: X-Auth-Key
    // ────────────────────────────────────────
    if (url.pathname === '/admin/orders' && request.method === 'GET') {
      const authKey = request.headers.get('X-Auth-Key');
      if (authKey !== env.ADMIN_KEY) {
        return new Response(JSON.stringify({ success: false, msg: '无权限' }), { status: 403, headers });
      }

      try {
        const orders = await getAllOrders(env);
        return new Response(JSON.stringify(orders), { headers });
      } catch (e) {
        return new Response(JSON.stringify([]), { headers });
      }
    }

    // ────────────────────────────────────────
    // 7. 重新计算已存激活码（恢复用）
    //    GET /admin/recalc?code=XXX  Header: X-Auth-Key
    // ────────────────────────────────────────
    if (url.pathname === '/admin/recalc' && request.method === 'GET') {
      const authKey = request.headers.get('X-Auth-Key');
      if (authKey !== env.ADMIN_KEY) {
        return new Response(JSON.stringify({ success: false, msg: '无权限' }), { status: 403, headers });
      }
      let mc = url.searchParams.get('code');
      if (!mc) return new Response(JSON.stringify({ success: false, msg: '缺少code' }), { headers });
      mc = mc.trim().toUpperCase();
      const code = await generateActivationCode(mc, env.HMAC_SECRET || env.ADMIN_KEY);
      return new Response(JSON.stringify({ success: true, machineCode: mc, activationCode: code }), { headers });
    }

    // ────────────────────────────────────────
    // 8. Decap CMS OAuth 认证入口
    //    GET /auth?provider=github
    // ────────────────────────────────────────
    if (url.pathname === '/auth') {
      const provider = url.searchParams.get('provider') || 'github';
      const client_id = env.GITHUB_CLIENT_ID;
      if (!client_id) {
        return new Response('Missing GITHUB_CLIENT_ID environment variable', { status: 500 });
      }

      const scope = url.searchParams.get('scope') || 'repo,user';
      // 使用 Decap CMS 传过来的 state 校验码以防止 CSRF
      const state = url.searchParams.get('state') || Math.random().toString(36).substring(2, 15);
      console.log("[OAuth Auth] CMS State:", url.searchParams.get('state'), "Final State:", state);
      
      const authUrl = `https://github.com/login/oauth/authorize?client_id=${client_id}&scope=${encodeURIComponent(scope)}&state=${state}`;
      return Response.redirect(authUrl, 302);
    }

    // ────────────────────────────────────────
    // 9. Decap CMS OAuth 回调
    //    GET /callback
    // ────────────────────────────────────────
    if (url.pathname === '/callback') {
      const code = url.searchParams.get('code');
      const state = url.searchParams.get('state'); // 提取 GitHub 返回 of state 校验码
      console.log("[OAuth Callback] GitHub State:", state);
      const client_id = env.GITHUB_CLIENT_ID;
      const client_secret = env.GITHUB_CLIENT_SECRET;

      if (!code) {
        return new Response(renderHTML('error', { message: '缺少 code 参数' }), {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }
      if (!client_id || !client_secret) {
        return new Response(renderHTML('error', { message: 'Worker 缺少 GITHUB_CLIENT_ID 或 GITHUB_CLIENT_SECRET 环境变量配置' }), {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }

      try {
        const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'wenjiang-oauth-worker'
          },
          body: JSON.stringify({ client_id, client_secret, code })
        });

        const tokenData = await tokenResponse.json();
        
        if (tokenData.error) {
          return new Response(renderHTML('error', { message: tokenData.error_description || tokenData.error }), {
            headers: { 'Content-Type': 'text/html; charset=utf-8' }
          });
        }

        const payload = {
          token: tokenData.access_token,
          provider: 'github',
          state: state
        };
        console.log("[OAuth Callback] Payload to CMS:", JSON.stringify(payload));

        return new Response(renderHTML('success', payload), {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      } catch (e) {
        return new Response(renderHTML('error', { message: e.message }), {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }
    }

    // 默认响应
    return new Response(JSON.stringify({ status: 'ok', service: '文匠激活服务' }), { headers });
  }
};

// ════════════════════════════════════════
// 工具函数
// ════════════════════════════════════════

const PAY_PRODUCTS = {
  filebeam_pro: { amount: '19.90', subject: 'FileBeam Pro 终身版' },
  bundle_pack: { amount: '29.80', subject: '双子星组合包（FileBeam Pro + 文匠）' },
  test_001: { amount: '0.01', subject: 'FileBeam 支付闭环测试' },
};

/**
 * 获取北京时间 (UTC+8) 格式化时间与紧凑时间戳
 */
function getBeijingTimeParts(date = new Date()) {
  const bj = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  const pad = (n) => String(n).padStart(2, '0');
  const yyyy = bj.getUTCFullYear();
  const mm = pad(bj.getUTCMonth() + 1);
  const dd = pad(bj.getUTCDate());
  const hh = pad(bj.getUTCHours());
  const mi = pad(bj.getUTCMinutes());
  const ss = pad(bj.getUTCSeconds());
  return {
    timestamp: `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`,
    compact: `${yyyy}${mm}${dd}${hh}${mi}${ss}`,
  };
}

/**
 * 生成唯一商户订单号，如 FB20261128163012A1B2C3
 */
function generateOutTradeNo() {
  const { compact } = getBeijingTimeParts();
  const randBytes = crypto.getRandomValues(new Uint8Array(3));
  const randHex = Array.from(randBytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase();
  return `FB${compact}${randHex}`;
}

/**
 * 兼容带/不带 PEM 头尾及换行符的 Base64 密钥转 ArrayBuffer
 */
function pemToArrayBuffer(pem) {
  const cleaned = String(pem || '')
    .replace(/-----BEGIN [A-Z0-9 ]+-----/g, '')
    .replace(/-----END [A-Z0-9 ]+-----/g, '')
    .replace(/\s+/g, '');
  const binary = atob(cleaned);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * 按参数名 ASCII 升序拼接待签名/待验签字符串
 */
function buildAlipaySignContent(params, excludeKeys = ['sign', 'sign_type']) {
  const excluded = new Set(excludeKeys);
  return Object.keys(params)
    .filter((k) => !excluded.has(k) && params[k] !== undefined && params[k] !== null && params[k] !== '')
    .sort()
    .map((k) => `${k}=${params[k]}`)
    .join('&');
}

/**
 * 纯 Web Crypto API 支付宝 RSA2 (PKCS8 + RSASSA-PKCS1-v1_5 + SHA-256) 签名
 */
async function signAlipayRSA2(content, privateKeyPem) {
  const keyBuffer = pemToArrayBuffer(privateKeyPem);
  const cryptoKey = await crypto.subtle.importKey(
    'pkcs8',
    keyBuffer,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5',
    cryptoKey,
    new TextEncoder().encode(content)
  );
  const bytes = new Uint8Array(signature);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * 纯 Web Crypto API 支付宝 RSA2 (SPKI + RSASSA-PKCS1-v1_5 + SHA-256) 验签
 */
async function verifyAlipayRSA2(content, signBase64, publicKeyPem) {
  if (!signBase64 || !publicKeyPem) return false;
  try {
    const keyBuffer = pemToArrayBuffer(publicKeyPem);
    const cryptoKey = await crypto.subtle.importKey(
      'spki',
      keyBuffer,
      { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
      false,
      ['verify']
    );
    const sigBinary = atob(String(signBase64).replace(/\s+/g, ''));
    const sigBytes = new Uint8Array(sigBinary.length);
    for (let i = 0; i < sigBinary.length; i++) {
      sigBytes[i] = sigBinary.charCodeAt(i);
    }
    return await crypto.subtle.verify(
      'RSASSA-PKCS1-v1_5',
      cryptoKey,
      sigBytes,
      new TextEncoder().encode(content)
    );
  } catch {
    return false;
  }
}

/**
 * 生成 FileBeam 无状态激活码：FB-<8位随机Hex>-<8位HMAC-SHA256>
 */
async function generateFileBeamCode(secretKey) {
  const payloadBytes = crypto.getRandomValues(new Uint8Array(4));
  const payload = Array.from(payloadBytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase();

  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secretKey),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const signature = await crypto.subtle.sign(
    'HMAC',
    key,
    new TextEncoder().encode(`FB-${payload}`)
  );
  const sig = Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .slice(0, 8)
    .toUpperCase();

  return `FB-${payload}-${sig}`;
}

/**
 * HMAC-SHA256 确定性算号
 * 同一机器码 + 同一密钥 → 永远生成同一激活码
 * 格式：XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX（32位十六进制，4组8位）
 */
async function generateActivationCode(machineCode, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(machineCode.toUpperCase()));
  const hex = [...new Uint8Array(sig)]
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase();
  return `${hex.slice(0, 8)}-${hex.slice(8, 16)}-${hex.slice(16, 24)}-${hex.slice(24, 32)}`;
}

/**
 * 遍历 KV 获取所有订单（最多 1000 条，分页安全）
 */
async function getAllOrders(env) {
  const orders = [];
  let cursor = null;

  do {
    const listOpts = { limit: 500 };
    if (cursor) listOpts.cursor = cursor;
    const list = await env.ACTIVATION_KV.list(listOpts);

    for (const key of list.keys) {
      const raw = await env.ACTIVATION_KV.get(key.name);
      if (raw) {
        try { orders.push(JSON.parse(raw)); } catch (e) {}
      }
    }

    cursor = list.list_complete ? null : list.cursor;
  } while (cursor);

  return orders;
}

/**
 * 发送飞书通知（非阻塞，失败不影响主流程）
 */
async function sendFeishu(env, text) {
  if (!env.FEISHU_WEBHOOK) return;
  await fetch(env.FEISHU_WEBHOOK, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ msg_type: 'text', content: { text } })
  }).catch(() => {});
}

/**
 * 提取来源信息：IP、Referer、UA、推断渠道
 */
function getSourceInfo(request, url) {
  const ip = request.headers.get('CF-Connecting-IP')
    || request.headers.get('X-Forwarded-For')
    || '未知';

  const referer = request.headers.get('Referer') || '';
  const ua = request.headers.get('User-Agent') || '';

  // 简化 UA：提取操作系统+浏览器关键词
  let uaShort = '未知设备';
  if (/iPhone|iPad/.test(ua))       uaShort = '📱 iOS';
  else if (/Android/.test(ua))      uaShort = '📱 Android';
  else if (/Windows/.test(ua))      uaShort = '💻 Windows';
  else if (/Mac OS X/.test(ua))     uaShort = '💻 macOS';
  else if (/Linux/.test(ua))        uaShort = '💻 Linux';
  // 浏览器
  if (/MicroMessenger/.test(ua))    uaShort += ' · 微信';
  else if (/Alipay/.test(ua))       uaShort += ' · 支付宝';
  else if (/Xianyu/.test(ua))       uaShort += ' · 闲鱼';
  else if (/Chrome/.test(ua))       uaShort += ' · Chrome';
  else if (/Safari/.test(ua))       uaShort += ' · Safari';

  // 推断渠道
  const source = url.searchParams.get('source') || '';
  let channel = 'unknown';
  if (source === 'xianyu')                          channel = 'xianyu';
  else if (source === 'website')                    channel = 'website';
  else if (/xianyu\.html/.test(referer))           channel = 'xianyu';
  else if (/activate\.html/.test(referer))         channel = 'website';
  else if (/wojingfang\.cn/.test(referer))         channel = 'website';
  else if (/Xianyu/.test(ua) || /淘宝/.test(ua))   channel = 'xianyu-app';
  else if (!referer)                                channel = 'direct/软件';

  return { ip, referer, ua, uaShort, channel };
}

/**
 * 渲染 Decap CMS OAuth 结果 HTML 页面
 */
function renderHTML(status, payload) {
  return `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8">
      <title>文匠 · CMS 授权中</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
          background: #080810;
          color: #e8e8f0;
        }
        .container {
          text-align: center;
          padding: 32px 24px;
          border-radius: 16px;
          background: #111120;
          border: 1px solid #1e1e35;
          box-shadow: 0 12px 40px rgba(0,0,0,0.5);
          max-width: 360px;
          width: 100%;
        }
        .status {
          font-size: 1.3rem;
          font-weight: 800;
          margin-bottom: 12px;
          background: ${status === 'success' ? 'linear-gradient(135deg, #4ade80, #22c55e)' : 'linear-gradient(135deg, #f87171, #ef4444)'};
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .desc {
          font-size: 0.9rem;
          color: #9898b0;
          line-height: 1.6;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="status">${status === 'success' ? '🎉 授权成功' : '❌ 授权失败'}</div>
        <div class="desc">${status === 'success' ? '已成功取得 GitHub 访问令牌，正在返回后台...' : (payload.message || '未知错误')}</div>
      </div>
      <script>
        (function() {
          function receiveMessage(e) {
            window.opener.postMessage(
              'authorization:github:${status}:${JSON.stringify(payload)}',
              e.origin
            );
          }
          window.addEventListener("message", receiveMessage, false);
          // 发起与 CMS 窗口的握手
          window.opener.postMessage("authorizing:github", "*");
        })()
      </script>
    </body>
    </html>
  `;
}
