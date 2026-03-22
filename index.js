function frame(index) {
  const c = document.getElementsByClassName('show-classdemo')[0];
  switch (index) {
    case 1:
      c.innerHTML = '<iframe src="blog.html" frameborder="1"></iframe>';
      break;
    case 2:
      c.innerHTML = '<iframe src="resume.html" frameborder="1"></iframe>';
      break;
    case 3:
      c.innerHTML = '<iframe src="/project/traffic.html" frameborder="1"></iframe>';
      break;
    case 4:
      c.innerHTML = '<iframe src="/project/track.html" frameborder="1"></iframe>';
      break;
    case 5:
      c.innerHTML = '<iframe src="/project/earthquake.html" frameborder="1"></iframe>';
      break;
  }
  console.log(index);
}