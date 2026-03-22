// sidebar.js - 注入共享侧边栏组件
(function () {
  const user = Auth.getUser();
  const currentPage = location.pathname.split('/').pop();

  const navItems = [
    { icon: '📊', label: '控制台',   href: 'dashboard.html' },
    { icon: '🏦', label: '我的账户', href: 'accounts.html' },
    { icon: '💸', label: '转账汇款', href: 'transfer.html' },
    { icon: '📈', label: '贷款中心', href: 'loan.html' },
    { icon: '⏰', label: '定期存款', href: 'fixed_deposit.html' },
    { icon: '📜', label: '交易流水', href: 'history.html' },
    { icon: '👤', label: '个人中心', href: 'profile.html' },
  ];

  const html = `
    <div class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">🏦</div>
        <span>星辰银行</span>
      </div>
      <nav class="nav-section">
        <div class="nav-label">主导航</div>
        ${navItems.map(item => `
          <a href="${item.href}" class="nav-item ${currentPage === item.href ? 'active' : ''}">
            <span class="icon">${item.icon}</span>${item.label}
          </a>`).join('')}
        <div class="nav-label mt-16">通知</div>
        <a href="notifications.html" class="nav-item ${currentPage==='notifications.html'?'active':''}">
          <span class="icon">🔔</span>消息通知<span id="notif-badge" class="text-warning text-sm"></span>
        </a>
      </nav>
      <div class="sidebar-footer">
        <div class="text-sm text-muted mb-16">${user.username || '用户'} 已登录</div>
        <button class="btn btn-secondary btn-sm btn-full" onclick="logout()">退出登录</button>
      </div>
    </div>`;

  const placeholder = document.getElementById('sidebar-placeholder');
  if (placeholder) placeholder.outerHTML = html;

  setTimeout(refreshNotifBadge, 200);
})();

function logout() {
  Auth.clear();
  location.href = 'login.html';
}
