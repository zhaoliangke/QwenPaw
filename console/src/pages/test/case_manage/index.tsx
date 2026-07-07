import { Card, Typography } from "antd";
import { CheckSquareOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function CaseManagePage() {
  return (
    <Card>
      <Title level={3}>
        <CheckSquareOutlined style={{ marginRight: 8 }} />
        测试用例管理
      </Title>
      <Paragraph>基于 Story 批量生成多维度测试用例，支持覆盖率分析和知识库增强。</Paragraph>
    </Card>
  );
}
