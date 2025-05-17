import './App.css'

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* Animated Gradient Background */}
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900 animate-gradient-x" />

      {/* Glassmorphism Card */}
      <div className="relative z-10 w-full max-w-full rounded-3xl bg-white/10 backdrop-blur-lg shadow-2xl border border-white/20 p-8 flex flex-col items-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white drop-shadow-lg mb-2 tracking-tight text-center">
          Live Camera Feed
        </h1>
        <p className="text-lg md:text-2xl text-blue-100 mb-6 text-center">
          Powered by OpenCV & Flask. Your camera, beautifully displayed.
        </p>
        <div className="w-screen rounded-2xl overflow-hidden border-4 border-blue-400/60 shadow-xl transition-all duration-300 hover:scale-105 hover:border-blue-300/90">
          <iframe
            src="http://localhost:5050"
            title="Camera Feed"
            className="w-full"
            style={{ minHeight: '600px', width: '48vw', maxHeight: '90vh' }}
            allow="camera"
          />
        </div>
      </div>

      {/* Optional: Add a soft glow effect */}
      <div className="absolute top-1/2 left-1/2 w-[1200px] h-[900px] -translate-x-1/2 -translate-y-1/2 bg-blue-500/20 rounded-full blur-3xl z-0 pointer-events-none" />
    </div>
  )
}

export default App
