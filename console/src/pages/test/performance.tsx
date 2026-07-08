import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface PerfResult {
  id: string;
  test_id: string;
  status: string;
  http_reqs: number;
  http_req_duration_p95: number;
  http_req_failed: number;
}

const mockResults: PerfResult[] = [];

const columns: ColumnsType<PerfResult> = [
  { title: "结果ID", dataIndex: "id", key: "id" },
  { title: "测试ID", dataIndex: "test_id", key: "test_id" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => <Tag color={val === "passed" ? "green" : "red"}>{val}</Tag>,
  },
  { title: "请求数", dataIndex: "http_reqs", key: "http_reqs" },
  { title: "P95 延迟", dataIndex: "http_req_duration_p95", key: "http_req_duration_p95", render: (v: number) => `${v.toFixed(0)}ms` },
  { title: "失败率", dataIndex: "http_req_failed", key: "http_req_failed", render: (v: number) => `${v.toFixed(2)}%` },
];

export default function PerformancePage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>性能测试</Title>
        <Paragraph type="secondary">
          集成 k6 执行负载/压力/尖峰/浸泡测试，收集关键指标并校验阈值。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">测试计划</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">已执行</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">通过</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">失败</Paragraph></Card></Col>
      </Row>

      <Card title="执行结果">
        <Table columns={columns} dataSource={mockResults} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
