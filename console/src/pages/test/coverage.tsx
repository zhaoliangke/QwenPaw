import { Card, Col, Progress, Row, Space, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface CoverageReport {
  id: string;
  iteration_id: string;
  line_rate: number;
  branch_rate: number;
  total_lines: number;
  covered_lines: number;
  created_at: string;
}

const mockReports: CoverageReport[] = [];

const columns: ColumnsType<CoverageReport> = [
  { title: "迭代ID", dataIndex: "iteration_id", key: "iteration_id" },
  {
    title: "行覆盖率",
    dataIndex: "line_rate",
    key: "line_rate",
    render: (val: number) => (
      <Progress percent={Math.round(val * 100)} size="small" status={val >= 0.8 ? "success" : "active"} />
    ),
  },
  {
    title: "分支覆盖率",
    dataIndex: "branch_rate",
    key: "branch_rate",
    render: (val: number) => (
      <Progress percent={Math.round(val * 100)} size="small" status={val >= 0.7 ? "success" : "exception"} />
    ),
  },
  { title: "覆盖行数", dataIndex: "covered_lines", key: "covered_lines" },
  { title: "总行数", dataIndex: "total_lines", key: "total_lines" },
  { title: "生成时间", dataIndex: "created_at", key: "created_at" },
];

export default function CoveragePage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>测试覆盖率分析</Title>
        <Paragraph type="secondary">
          集成 coverage.py 计算行/分支覆盖率，识别未覆盖代码路径，驱动测试用例补充。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Title level={2}>-</Title>
            <Paragraph type="secondary">平均行覆盖率</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>-</Title>
            <Paragraph type="secondary">平均分支覆盖率</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">未覆盖文件</Paragraph>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Title level={2}>0</Title>
            <Paragraph type="secondary">覆盖率报告</Paragraph>
          </Card>
        </Col>
      </Row>

      <Card title="覆盖率报告">
        <Table columns={columns} dataSource={mockReports} rowKey="id" pagination={{ pageSize: 10 }} />
      </Card>
    </Space>
  );
}
