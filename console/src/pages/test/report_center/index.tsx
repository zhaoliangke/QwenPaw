import { Card, Typography } from "antd";
import { BarChartOutlined } from "@ant-design/icons";

const { Title, Paragraph } = Typography;

export default function ReportCenterPage() {
  return (
    <Card>
      <Title level={3}>
        <BarChartOutlined style={{ marginRight: 8 }} />
        测试报告中心
      </Title>
      <Paragraph>查看历史测试报告，AI 自动分析高频缺陷和风险模块。</Paragraph>
    </Card>
  );
}
