import { useState } from "react"
import { Outlet, useNavigate, useParams } from "react-router-dom"
import SplitPane, { Pane } from "split-pane-react"
import "split-pane-react/esm/themes/default.css"
import ChatSidebar from "./ChatSidebar"

export default function ChatsLayout() {
    const [sizes, setSizes] = useState<(number | string)[]>([300, "auto"])
    const navigate = useNavigate()
    const { uuid } = useParams()

    return (
        <div style={{ height: "100vh" }}>
            <SplitPane
                split="vertical"
                sizes={sizes}
                onChange={setSizes}
                sashRender={() => <div style={{ width: 1, background: "#2a2a2a", cursor: "col-resize" }} />}
            >
                <Pane minSize={200} maxSize="40%">
                    <ChatSidebar
                        activeChatId={uuid ?? null}
                        onSelectAddFriend={() => navigate("/chats")}
                        onSelectChat={(id: string) => navigate(`/chats/${id}`)}
                    />
                </Pane>
                <Outlet />
            </SplitPane>
        </div>
    )
}