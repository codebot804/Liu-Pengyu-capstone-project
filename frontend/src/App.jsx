import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000'

function prettyLabel(value) {
  return value || 'N/A'
}

function HeroStat({ value, label }) {
  return (
    <div className="hero-stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  )
}

function PhotoCard({ photo, onDelete, deletingId }) {
  const imageUrl = `${API_BASE}${photo.file_url}`

  return (
    <article className="photo-card">
      <div className="photo-frame">
        <img src={imageUrl} alt={photo.caption || photo.original_name} className="thumb" />
        <div className="photo-overlay">
          <span className="pill">Smart Album</span>
          {photo.score !== undefined && photo.score !== null && (
            <span className="pill pill-score">Match {photo.score}</span>
          )}
        </div>
      </div>

      <div className="card-body">
        <div className="card-header-row">
          <div>
            <h3 title={photo.original_name}>{photo.original_name}</h3>
            <p className="caption">{photo.caption || 'No caption generated yet.'}</p>
          </div>
          <div className="card-actions">
            <a className="download-btn" href={imageUrl} download={photo.original_name} target="_blank" rel="noreferrer">
              Download
            </a>
            <button
              type="button"
              className="delete-btn"
              onClick={() => onDelete(photo.id)}
              disabled={deletingId === photo.id}
            >
              {deletingId === photo.id ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>

        <div className="tag-grid">
          <div className="tag-item"><span>Scene</span><strong>{prettyLabel(photo.scene)}</strong></div>
          <div className="tag-item"><span>Weather</span><strong>{prettyLabel(photo.weather)}</strong></div>
          <div className="tag-item"><span>People</span><strong>{prettyLabel(photo.people)}</strong></div>
          <div className="tag-item"><span>Actions</span><strong>{prettyLabel(photo.actions)}</strong></div>
          <div className="tag-item"><span>Objects</span><strong>{prettyLabel(photo.objects)}</strong></div>
          <div className="tag-item"><span>Mood</span><strong>{prettyLabel(photo.mood)}</strong></div>
        </div>
      </div>
    </article>
  )
}

export default function App() {
  const [photos, setPhotos] = useState([])
  const [query, setQuery] = useState('')
  const [selectedFiles, setSelectedFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState('browse')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  const title = useMemo(() => (
    mode === 'search' ? 'Search Results' : 'Album Gallery'
  ), [mode])

  const loadPhotos = async () => {
    try {
      const res = await axios.get(`${API_BASE}/photos`)
      setPhotos(res.data)
    } catch (err) {
      setError('Failed to load photos.')
    }
  }

  useEffect(() => {
    loadPhotos()
  }, [])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!selectedFiles.length) return

    const form = new FormData()
    selectedFiles.forEach((file) => form.append('files', file))

    setLoading(true)
    setError('')
    setSuccess('')
    try {
      await axios.post(`${API_BASE}/upload-multiple`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSelectedFiles([])
      const fileInput = document.getElementById('multi-upload-input')
      if (fileInput) fileInput.value = ''
      setMode('browse')
      setSuccess(`Successfully uploaded and analyzed ${selectedFiles.length} photo${selectedFiles.length > 1 ? 's' : ''}.`)
      await loadPhotos()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }


  const handleDelete = async (photoId) => {
    const confirmed = window.confirm('Are you sure you want to delete this photo?')
    if (!confirmed) return

    setDeletingId(photoId)
    setError('')
    setSuccess('')

    try {
      await axios.delete(`${API_BASE}/photo/${photoId}`)
      setPhotos((prev) => prev.filter((photo) => photo.id !== photoId))
      setSuccess('Photo deleted successfully.')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to delete photo.')
    } finally {
      setDeletingId(null)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      setMode('browse')
      loadPhotos()
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await axios.post(`${API_BASE}/search`, { query, top_k: 12 })
      setPhotos(res.data.results)
      setMode('search')
    } catch (err) {
      setError('Search failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="bg-orb orb-1" />
      <div className="bg-orb orb-2" />
      <div className="bg-orb orb-3" />

      <header className="hero-shell">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow">Capstone Demo</span>
            <h1>Intelligent Photo Album</h1>
            <p>
              Upload, understand, organize, search, and now download your photos in a cleaner,
              more polished interface.
            </p>
            <div className="hero-stats">
              <HeroStat value={photos.length} label="Photos in album" />
              <HeroStat value="AI" label="Caption + tags" />
              <HeroStat value="NL" label="Semantic search" />
            </div>
          </div>
          <div className="hero-card">
            <div className="hero-card-top">
              <span className="mini-pill">Upload</span>
              <span className="mini-pill">Search</span>
              <span className="mini-pill">Download</span>
            </div>
            <h3>Smarter visual memory</h3>
            <p>
              Designed for fast demo flow: upload multiple photos, retrieve results with natural
              language, and export any image directly from the result cards.
            </p>
          </div>
        </section>
      </header>

      <section className="panel-grid">
        <form className="panel panel-upload" onSubmit={handleUpload}>
          <div className="panel-heading">
            <h2>Upload Photos</h2>
            <span className="panel-badge">Multiple files supported</span>
          </div>

          <label htmlFor="multi-upload-input" className="upload-dropzone">
            <input
              id="multi-upload-input"
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
            />
            <div className="upload-icon">↑</div>
            <strong>Choose one or more images</strong>
            <span>JPG, PNG and other image files are supported.</span>
          </label>

          <div className="selected-files">
            {selectedFiles.length > 0 ? (
              selectedFiles.map((file) => (
                <div className="file-chip" key={`${file.name}-${file.size}`}>
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
              ))
            ) : (
              <p className="helper-text">No files selected yet.</p>
            )}
          </div>

          <button type="submit" disabled={loading || !selectedFiles.length}>
            {loading ? 'Processing...' : `Upload & Analyze${selectedFiles.length ? ` (${selectedFiles.length})` : ''}`}
          </button>
        </form>

        <form className="panel" onSubmit={handleSearch}>
          <div className="panel-heading">
            <h2>Search</h2>
            <span className="panel-badge">Natural language</span>
          </div>
          <input
            type="text"
            placeholder='e.g. "a girl playing volleyball on the beach"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <p className="helper-text">
            Use short descriptive text for the best results, such as people, scene, object, or mood.
          </p>
          <div className="row">
            <button type="submit" disabled={loading}>Search</button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setQuery('')
                setMode('browse')
                setSuccess('')
                setError('')
                loadPhotos()
              }}
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      {error && <p className="notice error">{error}</p>}
      {success && <p className="notice success">{success}</p>}

      <section className="content">
        <div className="content-header">
          <div>
            <span className="content-label">Research Results</span>
            <h2>{title}</h2>
          </div>
          <p>
            {mode === 'search'
              ? 'Showing the most relevant matches ranked by semantic similarity and structured tags.'
              : 'Browse all analyzed photos stored in your album.'}
          </p>
        </div>

        {photos.length === 0 ? (
          <div className="empty">
            <h3>No photos found yet</h3>
            <p>Upload a few images first, then try a natural language search.</p>
          </div>
        ) : (
          <div className="gallery">
            {photos.map((photo) => <PhotoCard key={photo.id} photo={photo} onDelete={handleDelete} deletingId={deletingId} />)}
          </div>
        )}
      </section>
    </div>
  )
}
