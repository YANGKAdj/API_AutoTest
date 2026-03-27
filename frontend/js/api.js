/**
 * api.js - 星辰银行前端 API 封装层
 * 统一处理 Token、错误提示、请求/响应格式
 */

const API_BASE = 'http://127.0.0.1:8000';

// ── Token 管理 ─────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('bank_token'),
  setToken: (t) => localStorage.setItem('bank_token', t),
  getUser:  () => JSON.parse(localStorage.getItem('bank_user') || '{}'),
  setUser:  (u) => localStorage.setItem('bank_user', JSON.stringify(u)),
  clear:    () => { localStorage.removeItem('bank_token'); localStorage.removeItem('bank_user'); },
  check:    () => { if (!Auth.getToken()) { location.href = '/frontend/login.html'; return false; } return true; },
};

// ── Toast 提示 ─────────────────────────────────────────
const Toast = {
  _container: null,
  init() {
    this._container = document.getElementById('toast-container') || (() => {
      const el = document.createElement('div');
      el.id = 'toast-container';
      el.className = 'toast-container';
      document.body.appendChild(el);
      return el;
    })();
  },
  show(msg, type = 'info', duration = 3000) {
    if (!this._container) this.init();
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.textContent = msg;
    this._container.appendChild(t);
    setTimeout(() => t.remove(), duration);
  },
  success: (m) => Toast.show(m, 'success'),
  error:   (m) => Toast.show(m, 'error'),
  info:    (m) => Toast.show(m, 'info'),
};

// ── HTTP 请求封装 ──────────────────────────────────────
async function request(method, path, body = null, requireAuth = true) {
  const headers = { 'Content-Type': 'application/json' };
  if (requireAuth) {
    const token = Auth.getToken();
    if (!token) { location.href = '/frontend/login.html'; return null; }
    headers['token'] = token;          // 兼容旧模块 (Account, Transaction)
    headers['authorization'] = token;  // 兼容新模块 (Loan, Profile, etc.)
  }
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API_BASE + path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      let msg = data?.detail?.msg || data?.detail || '请求失败';
      if (Array.isArray(msg)) msg = msg[0]?.msg || '参数校验失败';
      else if (typeof msg === 'object') msg = JSON.stringify(msg);
      Toast.error(msg);
      return null;
    }
    return data;
  } catch (e) {
    Toast.error('网络错误，请检查服务是否运行');
    return null;
  }
}

const get  = (path)        => request('GET',  path);
const post = (path, body)  => request('POST', path, body);
const put  = (path, body)  => request('PUT',  path, body);
const del  = (path)        => request('DELETE', path);

// ── 业务 API ──────────────────────────────────────────
const BankAPI = {
  // 认证
  login:    (u, p) => request('POST', '/api/auth/login',    { username: u, password: p }, false),
  register: (d)    => request('POST', '/api/auth/register', d, false),

  // 账户
  createAccount: (type) => post('/api/account/open', { account_type: type }),
  getAccounts:   ()     => get('/api/account/list'),
  getAccount:    (no)   => get(`/api/account/${no}`),
  getBalance:    (no)   => get(`/api/account/balance/${no}`),
  closeAccount:  (no)   => post(`/api/account/close/${no}`, {}),

  // 存取款
  deposit:  (account_no, amount) => post('/api/transaction/deposit',  { account_no, amount }),
  withdraw: (account_no, amount) => post('/api/transaction/withdraw', { account_no, amount }),

  // 转账
  transfer:      (from, to, amount, remark) => post('/api/transaction/transfer',            { from_account: from, to_account: to, amount, remark }),
  crossTransfer: (from, to_bank, to, amount) => post('/api/transaction/transfer/cross-bank', { from_account: from, to_bank_code: to_bank, to_account: to, amount }),

  // 贷款
  applyLoan:  (d)     => post('/api/loan/apply',       d),
  listLoans:  ()      => get('/api/loan/list'),
  getLoan:    (id)    => get(`/api/loan/${id}`),
  repayLoan:  (id, d) => post(`/api/loan/${id}/repay`, d),

  // 定期
  createFD: (d)   => post('/api/fixed-deposit/create',        d),
  listFDs:  ()    => get('/api/fixed-deposit/list'),
  withdrawFD: (id) => post(`/api/fixed-deposit/${id}/withdraw`, {}),

  // 流水
  history: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return get('/api/transactions/history' + (qs ? '?' + qs : ''));
  },

  // 个人资料
  getProfile:     ()  => get('/api/profile/'),
  updateProfile:  (d) => put('/api/profile/', d),
  changePassword: (d) => put('/api/profile/password', d),

  // 通知
  getNotifications: (unread) => get('/api/notifications/' + (unread ? '?unread_only=true' : '')),
  markRead:    (id) => put(`/api/notifications/${id}/read`, {}),
  markAllRead: ()   => put('/api/notifications/read-all',  {}),
};

// ── 格式化工具 ─────────────────────────────────────────
const fmt = {
  money: (v) => '¥ ' + Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2 }),
  date:  (s) => new Date(s).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
  txnType: { deposit: '存款', withdraw: '取款', transfer: '行内转账', cross_transfer: '跨行转账', loan_repay: '贷款还款' },
  status:  { active: '正常', frozen: '冻结', closed: '注销', settled: '已还清', broken: '已支取', matured: '已到期' },
};

// ── 更新侧边栏通知数量 ─────────────────────────────────
async function refreshNotifBadge() {
  const el = document.getElementById('notif-badge');
  if (!el) return;
  const res = await BankAPI.getNotifications(true);
  if (res) el.textContent = res.unread_count > 0 ? `(${res.unread_count})` : '';
}

window.Auth = Auth;
window.Toast = Toast;
window.BankAPI = BankAPI;
window.fmt = fmt;
window.refreshNotifBadge = refreshNotifBadge;
