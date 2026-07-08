import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface TestDataItem {
  id: string;
  name: string;
  description: string;
  product_line: string;
  item_count: number;
  created_at: string;
}

const mockData: TestDataItem[] = [];

const columns: ColumnsType<TestDataItem> = [
  { title: "名称", dataIndex: "name", key: "name" },
  { title: "描述", dataIndex: "description", key: "description" },
  {
    title: "产品线",
    dataIndex: "product_line",
    key: "product_line",
    render: (val: string) => val ? <Tag color="blue">{val}</Tag> : "-",
  },
  { title: "数据项数", dataIndex: "item_count", key: "item_count" },
  { title: "创建时间", dataIndex: "created_at", key: "created_at" },
];

export default function TestDataPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>测试数据管理</Title>
        <Paragraph type="secondary">
          管理测试数据集，支持 Schema 定义自动生成、CSV/JSON 导入、Faker 生成和变量替换。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">数据集总数</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">数据总行数</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">活跃迭代引用</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">变量模板数</Paragraph>
          </Card>
        </Col>
      </Row>

      <Card title="数据集列表">
        <Table columns={columns} dataSource={mockData} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
