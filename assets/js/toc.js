/* 芦苇博客 —— 文章目录生成(纯原生 JS,无外部依赖)
 * 扫描 main 内 h2/h3,生成嵌套目录;无 h2 时保持 nav 隐藏。
 * 标题 id 优先使用 kramdown auto_ids 生成的,缺失时自行生成(支持中文)。
 */
(function () {
  'use strict';

  var nav = document.getElementById('toc');
  var article = document.querySelector('main');
  if (!nav || !article) return;

  var headings = Array.prototype.slice.call(article.querySelectorAll('h2, h3'));
  var hasH2 = headings.some(function (h) { return h.tagName === 'H2'; });
  if (!hasH2) return; // 无 h2,保持 nav[hidden]

  var used = Object.create(null);

  function uniqueId(text, index) {
    var base = String(text).trim().toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\p{L}\p{N}_-]/gu, '')
      .replace(/-+/g, '-')
      .replace(/^-+|-+$/g, '');
    var id = base || 'section-' + index;
    var candidate = id;
    var i = 2;
    while (used[candidate]) candidate = id + '-' + i++;
    used[candidate] = true;
    return candidate;
  }

  var list = document.createElement('ol');
  list.className = 'toc-list';
  var currentLi = null;

  headings.forEach(function (h, i) {
    if (!h.id) h.id = uniqueId(h.textContent, i + 1);
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent.trim();
    a.className = h.tagName === 'H2' ? 'toc-h2' : 'toc-h3';
    var li = document.createElement('li');
    li.appendChild(a);

    if (h.tagName === 'H2') {
      list.appendChild(li);
      currentLi = li;
    } else if (currentLi) {
      var sub = currentLi.querySelector('ol');
      if (!sub) {
        sub = document.createElement('ol');
        currentLi.appendChild(sub);
      }
      sub.appendChild(li);
    } else {
      list.appendChild(li); // h3 出现在任何 h2 之前时平铺
    }
  });

  nav.appendChild(list);
  nav.removeAttribute('hidden');

  // 移动端「目录」折叠按钮
  var toggle = nav.querySelector('.toc-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
    });
  }

  // 滚动到视区时高亮对应目录项
  if ('IntersectionObserver' in window) {
    var links = {};
    list.querySelectorAll('a').forEach(function (a) {
      links[a.getAttribute('href').slice(1)] = a;
    });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        list.querySelectorAll('a.active').forEach(function (a) { a.classList.remove('active'); });
        var a = links[entry.target.id];
        if (a) a.classList.add('active');
      });
    }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 });
    headings.forEach(function (h) { observer.observe(h); });
  }
})();
