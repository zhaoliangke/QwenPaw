import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface ABResult {
  id: string;
  status: string;
  winner: string;
  conclusion: string;
}

const mockResults: ABResult[] = [];

const columns: ColumnsType<ABResult> = [
  { title: "结果ID", dataIndex: "id", key: "id" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const colors: Record<string, string> = { completed: "green", running: "blue", inconclusive: "orange" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  {
    title: "胜出方",
    dataIndex: "winner",
    key: "winner",
    render: (val: string) => val ? <Tag color="blue">{val}</Tag> : "-",
  },
  { title: "结论", dataIndex: "conclusion", key: "conclusion" },
];

export default function ABTestPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>A/B 测试辅助</Title>
        <Paragraph type="secondary">
          配置对照组和实验组，通过统计显著性分析 (t-test) 判断变体效果差异。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">测试数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">运行中</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">已完成</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">无结论</Paragraph></Card></Col>
      </Row>

      <Card title="分析结果">
        <Table columns={columns} dataSource={mockResults} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
