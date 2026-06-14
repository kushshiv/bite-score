export function useAuthModal() {
  const visible = useState('auth-modal-visible', () => false)
  const mode = useState<'login' | 'register'>('auth-modal-mode', () => 'login')

  function open(m: 'login' | 'register') {
    mode.value = m
    visible.value = true
  }

  function close() {
    visible.value = false
  }

  return { visible, mode, open, close }
}
