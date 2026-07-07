import { Card, Typography } from "antd";
import { BookOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function KnowledgeLibPage() {
  return (
    <Card>
      <Title level={3}>
        <BookOutlined style={{ marginRight: 8 }} />
        测试知识库
      </Title>
      <Paragraph>检索历史测试资产，按产品线、模块、迭代归档，支持知识蒸馏。</Paragraph>
    </Card>
  );
}
