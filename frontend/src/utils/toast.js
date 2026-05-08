export function showToast(msg) {
  window._toast?.show(msg, 'info')
}
export function showSuccessToast(msg) {
  window._toast?.show(msg, 'success')
}
export function showErrorToast(msg) {
  window._toast?.show(msg, 'error')
}
