import React from "react";

import { IconButton } from "@agentscope-ai/design";
import { SparkHistoryLine, SparkNewChatFill } from "@agentscope-ai/icons";
import {
  CompressOutlined,
  ExpandAltOutlined,
  MoreOutlined,
  OrderedListOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { Dropdown, Flex, Tooltip } from "antd";
import type { MenuProps } from "antd";
import { useCreateNewSession } from "../../hooks/useCreateNewSession";
import { useIsMobile } from "../../../../hooks/useIsMobile";

interface ChatActionGroupProps {
  /** Callback to toggle the right-side history panel */
  onToggleHistory?: () => void;
  /** Whether the history panel is currently visible */
  historyOpen?: boolean;
  isWideMode?: boolean;
  onToggleWideMode?: () => void;
  /** Callback to toggle the workflow panel */
  onToggleWorkflow?: () => void;
  /** Whether the workflow panel is currently visible */
  workflowOpen?: boolean;
}

const ChatActionGroup: React.FC<ChatActionGroupProps> = ({
  onToggleHistory,
  historyOpen = false,
  isWideMode = false,
  onToggleWideMode,
  onToggleWorkflow,
  workflowOpen = false,
}) => {
  const { t } = useTranslation();

  const createNewSession = useCreateNewSession();

  // Compact mode follows the viewport: collapse secondary actions only on
  // mobile. This saves space on phones while keeping actions visible on desktop.
  const isCompact = useIsMobile();

  // Build "more" dropdown items for compact mode: History, WideMode, Workflow.
  const moreItems: MenuProps["items"] = [];
  if (onToggleHistory) {
    moreItems.push({
      key: "history",
      icon: <SparkHistoryLine />,
      label: (
        <div style={{ textAlign: "center" }}>
          {t("chat.chatHistoryTooltip")}
        </div>
      ),
      onClick: () => onToggleHistory(),
    });
  }
  if (onToggleWideMode) {
    moreItems.push({
      key: "wideMode",
      icon: isWideMode ? <CompressOutlined /> : <ExpandAltOutlined />,
      label: (
        <div style={{ textAlign: "center" }}>
          {isWideMode ? t("chat.normalModeTooltip") : t("chat.wideModeTooltip")}
        </div>
      ),
      onClick: () => onToggleWideMode(),
    });
  }
  if (onToggleWorkflow) {
    moreItems.push({
      key: "workflow",
      icon: (
        <OrderedListOutlined
          style={
            workflowOpen
              ? { color: "var(--color-primary, #ff9d4d)" }
              : undefined
          }
        />
      ),
      label: (
        <div style={{ textAlign: "center" }}>
          {t("chat.workflowPanelTooltip")}
        </div>
      ),
      onClick: () => onToggleWorkflow(),
    });
  }

  return (
    <Flex gap={8} align="center">
      {/* Essential actions always visible */}
      <Tooltip title={t("chat.newChatTooltip")} mouseEnterDelay={0.5}>
        <IconButton
          bordered={false}
          icon={<SparkNewChatFill />}
          onClick={createNewSession}
        />
      </Tooltip>

      {/* History + Workflow + WideMode: inline when NOT compact */}
      {!isCompact && onToggleHistory && (
        <Tooltip title={t("chat.chatHistoryTooltip")} mouseEnterDelay={0.5}>
          <IconButton
            bordered={false}
            icon={<SparkHistoryLine />}
            style={
              historyOpen
                ? { color: "var(--color-primary, #ff9d4d)" }
                : undefined
            }
            onClick={onToggleHistory}
          />
        </Tooltip>
      )}
      {!isCompact && onToggleWorkflow && (
        <Tooltip title={t("chat.workflowPanelTooltip")} mouseEnterDelay={0.5}>
          <IconButton
            bordered={false}
            icon={<OrderedListOutlined />}
            style={
              workflowOpen
                ? { color: "var(--color-primary, #ff9d4d)" }
                : undefined
            }
            onClick={onToggleWorkflow}
          />
        </Tooltip>
      )}
      {!isCompact && onToggleWideMode && (
        <Tooltip
          title={
            isWideMode ? t("chat.normalModeTooltip") : t("chat.wideModeTooltip")
          }
          mouseEnterDelay={0.5}
        >
          <IconButton
            bordered={false}
            icon={isWideMode ? <CompressOutlined /> : <ExpandAltOutlined />}
            onClick={onToggleWideMode}
          />
        </Tooltip>
      )}

      {/* Compact mode: collapse History/WideMode/Workflow into more dropdown */}
      {isCompact && moreItems.length > 0 && (
        <Dropdown
          menu={{ items: moreItems }}
          trigger={["click"]}
          placement="bottomRight"
        >
          <IconButton bordered={false} icon={<MoreOutlined />} />
        </Dropdown>
      )}
    </Flex>
  );
};

export default ChatActionGroup;
