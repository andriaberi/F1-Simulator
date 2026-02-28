import formulaOneLogo from '../../images/f1-logo.png';

function Navbar({ pageName }) {
    const pages = [
        { id: 'home', name: 'Home' },
        { id: 'about', name: 'About' },
    ];

    return (
        <nav className="navbar" id="navbar">
            <div className="nav-logo">
                <img src={formulaOneLogo} alt="Nav Logo" />
                Simulator
            </div>
            <ul className="nav-list">
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
        </nav>
    );
}

export default Navbar;