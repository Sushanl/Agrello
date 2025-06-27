import { useState } from 'react'
import Header from './Header';
import Dropzone from './Dropzone';
import '../styles/App.css'

export default function App() {

    const [file, setFile] = useState(null)

    
    return (
    <div className='main'>
    <Header />
    <Dropzone file={file} setFile={setFile}/>
    </ div>
    )

  
}

