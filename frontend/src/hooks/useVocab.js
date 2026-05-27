import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../api'

export function useVocab() {
  const [ragas, setRagas] = useState([])
  const [talas, setTalas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      axios.get(`${API_BASE}/api/ragas`),
      axios.get(`${API_BASE}/api/talas`),
    ]).then(([r, t]) => {
      setRagas(r.data)
      setTalas(t.data)
      setLoading(false)
    }).catch((err) => {
      console.error('[useVocab] Failed to fetch ragas/talas from', API_BASE || '(no API_BASE set)', err?.message)
      setError(`Cannot reach backend. Check VITE_API_URL env var. (${API_BASE || 'empty'})`)
      setLoading(false)
    })
  }, [])

  return { ragas, talas, loading, error }
}
