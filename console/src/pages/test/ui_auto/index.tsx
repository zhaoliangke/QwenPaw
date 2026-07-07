import { Card, Typography } from "antd";
import { PlayCircleOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function UIAutoPage() {
  return (
    <Card>
      <Title level={3}>
        <PlayCircleOutlined style={{ marginRight: 8 }} />
        UI 自动化脚本
      </Title>
      <Paragraph>基于自然语言生成 Playwright 自动化脚本，支持在线调试和视觉定位。</Paragraph>
    </Card>
  );
}
