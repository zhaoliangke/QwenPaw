import { Card, Typography } from "antd";
import { ThunderboltOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function TestExecPage() {
  return (
    <Card>
      <Title level={3}>
        <ThunderboltOutlined style={{ marginRight: 8 }} />
        测试执行调度
      </Title>
      <Paragraph>批量执行测试用例，实时查看执行进度、截图和日志。</Paragraph>
    </Card>
  );
}
