"""Bounded, static attention behavior for explicit Delivery transitions."""

from architecture_governance_copilot.ui_support import DELIVERY_ATTENTION_TARGETS


def delivery_focus_markup(target: str, sequence: int) -> str:
    """Allow only internal anchors and numeric tokens, never user-controlled script content."""
    if target not in DELIVERY_ATTENTION_TARGETS or type(sequence) is not int or sequence < 1:
        raise ValueError("Invalid delivery focus request.")
    return """<script>
(() => {
  // Event TOKEN: one-shot focus after an explicit action, including repeated previews.
  const id = 'agc-delivery-TARGET';
  let observer;
  let timer;
  let completed = false;
  const focus = () => {
    const destination = document.getElementById(id);
    if (!destination || completed) return false;
    completed = true;
    if (observer) observer.disconnect();
    clearTimeout(timer);
    requestAnimationFrame(() => requestAnimationFrame(() => {
      destination.focus({preventScroll: true});
      destination.scrollIntoView({block: 'start', behavior:
        matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
    }));
    return true;
  };
  if (!focus()) {
    observer = new MutationObserver(focus);
    observer.observe(document.body, {childList: true, subtree: true});
    timer = setTimeout(() => observer.disconnect(), 3000);
  }
})();
</script>""".replace("TARGET", target).replace("TOKEN", str(sequence))
