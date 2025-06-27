import React, {useCallback}  from 'react'
import {useDropzone} from 'react-dropzone'
import '../styles/Dropzone.css'
import { useState } from 'react'



export default function MyDropzone({file, setFile}) {
  const onDrop = useCallback(acceptedFiles => {
    setFile(acceptedFiles[0])
    console.log(file)
  }, [])

  const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,})

  return (
    <>
        <div {...getRootProps()} className='dropzone dropzoneActive'>
        <input {...getInputProps()}/>
        {
            isDragActive ?
            <p className='drag-words'>Drop the files here ...</p> :
            <p className='drag-words'>Drag 'n' drop some files here, or click to select files</p>
        }
        </div>

        {
            file ? 
            <>
            <div className="preview-tab">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                    <div className="preview-icon" />
                    <p>{file.name}</p>
                    <button className='submit-button'>Submit</button>
                    </div>
                    
            </div>
            
            </>
            : null
        }
    </>
  )
}
