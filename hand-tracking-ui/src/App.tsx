import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { HandRaisedIcon, VideoCameraIcon } from '@heroicons/react/24/outline'
import './App.css'

function App() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [fps, setFps] = useState(0)
  const [handCount, setHandCount] = useState(0)

  useEffect(() => {
    let frameCount = 0
    let lastTime = performance.now()
    
    const updateFPS = () => {
      frameCount++
      const currentTime = performance.now()
      const elapsed = currentTime - lastTime
      
      if (elapsed >= 1000) {
        setFps(Math.round((frameCount * 1000) / elapsed))
        frameCount = 0
        lastTime = currentTime
      }
      
      requestAnimationFrame(updateFPS)
    }
    
    updateFPS()
  }, [])

  useEffect(() => {
    if (!isStreaming) return

    const fetchHandCount = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/hand-count')
        const data = await response.json()
        setHandCount(data.count)
      } catch (error) {
        console.error('Error fetching hand count:', error)
      }
    }

    const interval = setInterval(fetchHandCount, 100)
    return () => clearInterval(interval)
  }, [isStreaming])

  return (
    <div className="min-h-screen bg-secondary">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-primary mb-2">
            Hand Tracking
          </h1>
          <p className="text-gray-600">
            Real-time hand tracking using computer vision
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="relative aspect-video">
              <img
                src="http://localhost:8080/video_feed"
                alt="Video Feed"
                className="w-full h-full object-contain"
              />
              <div className="absolute top-4 left-4 flex gap-4">
                <div className="bg-black/50 text-white px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  <VideoCameraIcon className="w-4 h-4" />
                  {fps} FPS
                </div>
                <div className="bg-black/50 text-white px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  <HandRaisedIcon className="w-4 h-4" />
                  {handCount} Hands
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 flex justify-center gap-4">
            <button
              type="button"
              onClick={() => setIsStreaming(!isStreaming)}
              className="btn btn-primary"
            >
              {isStreaming ? 'Stop Tracking' : 'Start Tracking'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
