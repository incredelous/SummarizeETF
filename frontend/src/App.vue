<template>
  <div class="layout">
    <header class="topbar">
      <div class="brand">SummarizeETF Web</div>
      <nav>
        <RouterLink to="/">指数列表</RouterLink>
        <RouterLink to="/stats">统计视图</RouterLink>
      </nav>
    </header>
    <main class="page">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f7f4ea, #dde9ef);
}
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #1f3c4d;
  color: #fff;
}
.brand {
  font-size: 18px;
  font-weight: 700;
}
nav {
  display: flex;
  gap: 16px;
}
a {
  color: #d9edf6;
  text-decoration: none;
}
a.router-link-active {
  color: #ffe7a3;
}
.page {
  padding: 20px;
}
</style>

