import AdminDashboard from './components/AdminDashboard'

function App() {
    return (
        <div className="app-container">
            <header className="app-header">
                <div className="logo">AdminPanel</div>
                <div className="user-profile">
                    <div className="avatar">AD</div>
                    <span>Administrator</span>
                </div>
            </header>
            <main className="app-main">
                <AdminDashboard />
            </main>
        </div>
    )
}

export default App
