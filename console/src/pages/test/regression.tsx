import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface RegressionPlan {
  id: string;
  base_ref: string;
  head_ref: string;
  total_cases: number;
  selected_count: number;
  estimated_time_saved: number;
  created_at: string;
}

const mockPlans: RegressionPlan[] = [];

const columns: ColumnsType<RegressionPlan> = [
  { title: "基准版本", dataIndex: "base_ref", key: "base_ref" },
  { title: "目标版本", dataIndex: "head_ref", key: "head_ref" },
  { title: "总用例数", dataIndex: "total_cases", key: "total_cases" },
  { title: "选中用例", dataIndex: "selected_count", key: "selected_count" },
  {
    title: "预估节省",
    dataIndex: "estimated_time_saved",
    key: "estimated_time_saved",
    render: (val: number) => <Tag color="green">{val.toFixed(0)}%</Tag>,
  },
  { title: "创建时间", dataIndex: "created_at", key: "created_at" },
];

export default function RegressionPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>智能回归选择</Title>
        <Paragraph type="secondary">
          分析 git diff 确定代码变更范围，智能选择受影响的测试用例，减少回归测试执行时间。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">回归计划</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">累计执行</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>-</Title>
            <Paragraph type="secondary">平均节省时间</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>-</Title>
            <Paragraph type="secondary">平均精准度</Paragraph>
          </Card>
        </Col>
      </Row>

      <Card title="回归计划列表">
        <Table columns={columns} dataSource={mockPlans} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
