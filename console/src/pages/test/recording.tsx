import { Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface Recording {
  id: string;
  case_id: string;
  status: string;
  duration_ms: number;
  file_size_bytes: number;
}

const mockRecordings: Recording[] = [];

const columns: ColumnsType<Recording> = [
  { title: "录制ID", dataIndex: "id", key: "id" },
  { title: "用例ID", dataIndex: "case_id", key: "case_id" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (val: string) => {
      const colors: Record<string, string> = { completed: "green", recording: "blue", failed: "red" };
      return <Tag color={colors[val] || "default"}>{val}</Tag>;
    },
  },
  {
    title: "时长",
    dataIndex: "duration_ms",
    key: "duration_ms",
    render: (val: number) => val ? `${(val / 1000).toFixed(1)}s` : "-",
  },
  {
    title: "文件大小",
    dataIndex: "file_size_bytes",
    key: "file_size_bytes",
    render: (val: number) => val ? `${(val / 1024).toFixed(0)} KB` : "-",
  },
];

export default function RecordingPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>执行视频录制</Title>
        <Paragraph type="secondary">
          通过 Playwright Trace 录制测试执行过程，支持 Trace Viewer 查看和报告嵌入。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">录制总数</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">已完成</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">录制中</Paragraph></Card></Col>
        <Col span={6}><Card><Title level={2}>0</Title><Paragraph type="secondary">总文件大小</Paragraph></Card></Col>
      </Row>

      <Card title="录制列表">
        <Table columns={columns} dataSource={mockRecordings} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
