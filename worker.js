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
      const state = Math.random().toString(36).substring(2, 15);
      
      const authUrl = `https://github.com/login/oauth/authorize?client_id=${client_id}&scope=${encodeURIComponent(scope)}&state=${state}`;
      return Response.redirect(authUrl, 302);
    }

    // ────────────────────────────────────────
    // 9. Decap CMS OAuth 回调
    //    GET /callback
    // ────────────────────────────────────────
    if (url.pathname === '/callback') {
      const code = url.searchParams.get('code');
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
          provider: 'github'
        };

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
