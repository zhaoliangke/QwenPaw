import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface DiffResult {
  id: string;
  status: string;
  diff_percentage: number;
  diff_pixels: number;
  baseline_path: string;
  current_path: string;
}

const mockResults: DiffResult[] = [];

const columns: ColumnsType<DiffResult> = [
  { title: "结果ID", dataIndex: "id", key: "id" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const colors: Record<string, string> = { match: "green", different: "red", baseline_missing: "orange", error: "default" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  {
    title: "差异百分比",
    dataIndex: "diff_percentage",
    key: "diff_percentage",
    render: (val: number) => <span style={{ color: val > 0.1 ? "red" : "green" }}>{(val * 100).toFixed(2)}%</span>,
  },
  { title: "差异像素", dataIndex: "diff_pixels", key: "diff_pixels" },
];

export default function VisualDiffPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>视觉回归测试</Title>
        <Paragraph type="secondary">
          使用 Playwright 捕获页面截图，通过像素级 diff 检测 UI 变更，支持基线更新和差异高亮。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">测试计划</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">已执行</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">匹配</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">差异</Paragraph></Card></Col>
      </Row>

      <Card title="Diff 结果">
        <Table columns={columns} dataSource={mockResults} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
