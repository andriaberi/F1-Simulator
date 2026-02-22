import Navbar from '../includes/navbar'

function Home() {
    return (
        <>
           <Navbar pageName="home"/>
            <div className="main">
                <aside className="left"></aside>
                <aside className="right"></aside>
            </div>
        </>
    );
}

export default Home;