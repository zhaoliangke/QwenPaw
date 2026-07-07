import { Card, Typography } from "antd";
import { FileTextOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function PrdAnalysisPage() {
  return (
    <Card>
      <Title level={3}>
        <FileTextOutlined style={{ marginRight: 8 }} />
        需求解析 & Story 管理
      </Title>
      <Paragraph>上传 PRD 文档、OpenAPI 规范或 Figma 链接，AI 自动解析需求并生成 User Story。</Paragraph>
    </Card>
  );
}
