import { Card, Typography } from "antd";
import { RocketOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function IterationPage() {
  return (
    <Card>
      <Title level={3}>
        <RocketOutlined style={{ marginRight: 8 }} />
        迭代管理
      </Title>
      <Paragraph>管理测试迭代：创建、状态流转、基线快照、变更对比、Jira 同步。</Paragraph>
    </Card>
  );
}
