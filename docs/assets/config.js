window.$docsify = {
  name: '学习笔记',
  nameLink: '#/',
  loadSidebar: true,
  subMaxLevel: 2,
  auto2top: true,
  relativePath: true,
  routerMode: 'hash',
  notFoundPage: true,
  alias: { '/.*/_sidebar.md': '/_sidebar.md' },
  search: {
    paths: 'auto',
    placeholder: '搜索笔记…',
    noData: '没有找到相关笔记',
    depth: 3,
    maxAge: 60000,
    namespace: 'personal-learning-notes',
    resultSource: 'page'
  },
  latex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    overflowScroll: true,
    customOptions: { throwOnError: false, strict: 'warn', trust: false }
  }
};
