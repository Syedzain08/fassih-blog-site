module.exports = {
  theme: {
    extend: {
      keyframes: {
        slideIn: { '0%': { transform: 'translateY(-100%)', opacity: '0' }, '100%': { transform: 'translateY(0)', opacity: '1' } },
        spinOnce: { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } }
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out forwards',
        'spin-once': 'spinOnce 0.3s linear forwards'
      }
    }
  },
  plugins: [],
};