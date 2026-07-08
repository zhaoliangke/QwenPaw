import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface ApiCase {
  id: string;
  name: string;
  method: string;
  url: string;
  status: string;
}

const mockCases: ApiCase[] = [];

const columns: ColumnsType<ApiCase> = [
  { title: "用例名称", dataIndex: "name", key: "name" },
  {
    title: "方法",
    dataIndex: "method",
    key: "method",
    render: (val: string) => {
      const colors: Record<string, string> = { GET: "green", POST: "blue", PUT: "orange", DELETE: "red", PATCH: "purple" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  { title: "URL", dataIndex: "url", key: "url" },
  {
    title: "最近执行",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const m: Record<string, string> = { passed: "green", failed: "red", pending: "default" };
      return <Tag color={m[val] || "default"}>{val || "-"}</Tag>;
    },
  },
];

export default function ApiTestPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>API 接口测试</Title>
        <Paragraph type="secondary">
          创建 API 测试用例，支持 RESTful 接口的请求发送、响应断言和批量套件执行。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">测试用例</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">测试套件</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">通过率</Paragraph></Card>
        </Col>
        <Col span={6}>
          <Card><Title level={2}>0</Title><Paragraph type="secondary">平均响应</Paragraph></Card>
        </Col>
      </Row>

      <Card title="API 用例列表">
        <Table columns={columns} dataSource={mockCases} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
