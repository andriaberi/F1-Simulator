import formulaOneLogo from '../../images/f1-logo.png';
import {useState} from "react";

function Navbar({ pageName }) {
    const [open, setOpen] = useState(false);

    const pages = [
        { id: 'home', name: 'Home' },
        { id: 'about', name: 'About' },
    ];

    const toggleOpen = () => {
      setOpen(prev => !prev); // toggle to opposite value
    };

    return (
        <>
        <nav className="navbar" id="navbar">
            <div className="nav-logo">
                <img src={formulaOneLogo} alt="Nav Logo" />
                Simulator
            </div>
            <ul className={`nav-list ${ open ? 'open' : ''}`}>
                {pages.map((page) => (
                    <li
                        key={page.id}
                        id={page.id}
                        className={`nav-item ${pageName === page.id ? 'active' : ''}`}
                    >
                        <a href={`#${page.id}`}>{page.name}</a>
                    </li>
                ))}
            </ul>
            <div className="nav-toggler" onClick={toggleOpen}>
                <i className={`bi ${open ? 'bi-list' : 'bi-x'}`}></i>
            </div>
        </nav>
        </>
    );
}

export default Navbar;