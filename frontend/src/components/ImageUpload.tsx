import { useEffect, useId, useRef, useState } from 'react'
import { ImagePlus, Upload, X } from 'lucide-react'

export default function ImageUpload({
  file,
  onChange,
  disabled = false,
}: {
  file: File | null
  onChange: (file: File | null) => void
  disabled?: boolean
}) {
  const id = useId()
  const input = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState('')
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => {
    if (!file) {
      setPreview('')
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])
  function accept(value?: File) {
    if (disabled || !value) return
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(value.type)) {
      setError('Choose a JPG, PNG or WebP image.')
      return
    }
    if (value.size > 8 * 1024 * 1024) {
      setError('Choose a photo smaller than 8 MB.')
      return
    }
    setError('')
    onChange(value)
  }
  return (
    <div className="upload-field">
      <label htmlFor={id}>
        Item photo <span className="optional">Optional</span>
      </label>
      <input
        ref={input}
        id={id}
        className="sr-only"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        disabled={disabled}
        onChange={(e) => {
          accept(e.target.files?.[0])
          e.target.value = ''
        }}
        aria-describedby={`${id}-hint`}
      />
      {file ? (
        <div className="upload-preview">
          {preview && <img src={preview} alt="Selected photo preview" />}
          <div>
            <strong>{file.name}</strong>
            <p>{(file.size / 1024 / 1024).toFixed(2)} MB · Ready to upload</p>
            <button
              className="text-link"
              type="button"
              disabled={disabled}
              onClick={() => input.current?.click()}
            >
              Choose a different photo
            </button>
          </div>
          <button
            type="button"
            className="icon-button"
            aria-label="Remove photo"
            disabled={disabled}
            onClick={() => onChange(null)}
          >
            <X size={18} />
          </button>
        </div>
      ) : (
        <button
          type="button"
          className={`upload-zone ${dragging ? 'dragging' : ''}`}
          disabled={disabled}
          onClick={() => input.current?.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            accept(e.dataTransfer.files[0])
          }}
        >
          <span className="upload-icon">
            <ImagePlus size={24} />
          </span>
          <strong>
            Drop your photo here, or <span>browse files</span>
          </strong>
          <span id={`${id}-hint`}>JPG, PNG or WebP · Up to 8 MB</span>
          <Upload className="upload-arrow" size={17} />
        </button>
      )}
      {error && (
        <p className="field-error" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
