import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="w-full max-w-6xl">
        <video
          autoPlay
          playsInline
          muted
          className="w-full h-auto"
        >
          <source src="http://localhost:8080/video_feed" type="multipart/x-mixed-replace" />
        </video>
      </div>
    </div>
  )
}

export default App
