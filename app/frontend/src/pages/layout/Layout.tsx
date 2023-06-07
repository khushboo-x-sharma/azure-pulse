import { Outlet, NavLink, Link } from "react-router-dom";

import github from "../../assets/github.svg";
import ambg_logo from "../../assets/ambg_logo_white.svg";

import styles from "./Layout.module.css";

const Layout = () => {
    return (
        <div className={styles.layout}>
            <header className={styles.header} role={"banner"}>
                <div className={styles.headerContainer}>
                    <Link to="/" className={styles.headerTitleContainer}>
                        <img
                            src={ambg_logo}
                            alt="AMBG logo"
                            // aria-label="Link to github repository"
                            width="100px"
                            height="100px"
                            // className={styles.githubLogo}
                        />
                        {/* <h3 className={styles.headerTitle}>GPT + Enterprise data | Sample</h3> */}
                        {/* <h3 className={styles.headerTitle}>Azure Pulse</h3> */}
                    </Link>
                    <nav>
                        <ul className={styles.headerNavList}>
                            <h3 className={styles.headerTitle}>Azure Pulse</h3>
                            {/* <li>
                                <NavLink to="/" className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}>
                                    Chat
                                </NavLink>
                            </li>
                            <li className={styles.headerNavLeftMargin}>
                                <NavLink to="/qa" className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}>
                                    Ask a question
                                </NavLink>
                            </li> */}
                            <li className={styles.headerNavLeftMargin}>
                                <h4 className={styles.headerTitle}>Powered by AMBG</h4>
                                <a
                                    href="https://github.com/AMBGASG/DATA.AI-Azure-OpenAI-Microsoft-Advisor-Bot"
                                    target={"_blank"}
                                    title="Github repository link"
                                >
                                    <img
                                        src={github}
                                        alt="Github logo"
                                        aria-label="Link to github repository"
                                        width="20px"
                                        height="20px"
                                        className={styles.githubLogo}
                                    />
                                </a>
                            </li>
                        </ul>
                    </nav>
                    {/* <h4 className={styles.headerRightText}>Azure OpenAI + Cognitive Search</h4> */}
                </div>
            </header>

            <Outlet />
        </div>
    );
};

export default Layout;
