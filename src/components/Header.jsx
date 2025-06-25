import logo from '../assets/logo.png';
import '../styles/Header.css';

export default function Header() {
    return (
        <header className='header'>
            <img src={logo} className='logo'></img>
        </header>
    )
}