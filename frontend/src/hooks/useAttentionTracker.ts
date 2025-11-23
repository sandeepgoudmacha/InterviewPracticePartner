import * as faceapi from 'face-api.js'
import * as tf from '@tensorflow/tfjs'
import { useEffect, useState, useRef } from 'react'

export function useAttentionTracker(videoRef: React.RefObject<HTMLVideoElement>) {
  const [attention, setAttention] = useState<number>(1)
  const focusedCountRef = useRef<number>(0)
  const distractedCountRef = useRef<number>(0)

  useEffect(() => {
    let intervalId: NodeJS.Timeout

    const loadModels = async () => {
      const MODEL_URL = '/models'

      try {
        // ✅ Initialize TensorFlow.js backend
        await tf.setBackend('webgl').catch(() => tf.setBackend('cpu'))
        await tf.ready()

        // ✅ Load face-api.js models
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODEL_URL)
        ])
      } catch (err) {
        console.error('Failed to load models:', err)
      }
    }

    const checkAttention = async () => {
      if (!videoRef.current || videoRef.current.readyState !== 4) {
        return
      }

      try {
        // Simple approach: just check if face is detected
        const detections = await faceapi
          .detectSingleFace(videoRef.current, new faceapi.TinyFaceDetectorOptions())
          .withFaceLandmarks(false)

        if (detections) {
          // Face detected - increment focused counter
          focusedCountRef.current++
          distractedCountRef.current = 0

          // After 2 consecutive detections, mark as focused
          if (focusedCountRef.current >= 2 && attention !== 1) {
            setAttention(1)
            focusedCountRef.current = 0
          }
        } else {
          // Face not detected - increment distracted counter
          distractedCountRef.current++
          focusedCountRef.current = 0

          // After 3 consecutive non-detections, mark as distracted
          if (distractedCountRef.current >= 3 && attention !== 0) {
            setAttention(0)
            distractedCountRef.current = 0
          }
        }
      } catch (error) {
        console.error('Attention tracking error:', error)
      }
    }

    loadModels().then(() => {
      // Check every 1 second
      intervalId = setInterval(checkAttention, 1000)
    })

    return () => clearInterval(intervalId)
  }, [videoRef, attention])

  return attention
}
