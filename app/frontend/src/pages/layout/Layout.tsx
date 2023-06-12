import { Outlet, NavLink, Link } from "react-router-dom";
import { BotSparkleFilled } from "@fluentui/react-icons";
import github from "../../assets/github.svg";
import ambg_logo from "../../assets/ambg_logo_white.svg";

import styles from "./Layout.module.css";

const Layout = () => {
    return (
        <div className={styles.layout}>
            <header className={styles.header} role={"banner"}>
                <div className={styles.headerContainer}>
                    <Link to="https://myasg.accenture.com/asg-technology/ambg-asg/?r" className={styles.headerLeft} title="AMBG ASG">
                        <img src={ambg_logo} alt="AMBG logo" width="100px" height="100px" />
                    </Link>
                    <li className={styles.headerCentre}>
                        <BotSparkleFilled fontSize={"40px"} primaryFill={"rgba(140, 20, 252,1)"} aria-hidden="true" aria-label="Pulse logo" />
                        {/* </li>
                    <li className={styles.headerCentre}> */}
                        <h1 className={styles.headerTitle}>Azure Pulse</h1>
                    </li>
                    {/* <h5 className={styles.headerTitle}>Powered by AMBG</h5> */}
                    <li className={styles.headerRight}>
                        <a href="https://github.com/AMBGASG/DATA.AI-Azure-OpenAI-Microsoft-Advisor-Bot" target={"_blank"} title="Github repository link">
                            <img
                                src={github}
                                alt="Github logo"
                                aria-label="Link to github repository"
                                width="30px"
                                height="30px"
                                className={styles.githubLogo}
                            />
                        </a>
                    </li>
                </div>
            </header>

            <Outlet />
        </div>
    );
};

export default Layout;
