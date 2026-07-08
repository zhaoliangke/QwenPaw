import { Progress, Card, Col, Row, Space, Statistic, Table, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";

const { Title, Paragraph } = Typography;

interface ModuleCoverage {
  module: string;
  case_count: number;
  coverage_rate: number;
}

const mockModules: ModuleCoverage[] = [];

const columns: ColumnsType<ModuleCoverage> = [
  { title: "模块", dataIndex: "module", key: "module" },
  { title: "用例数", dataIndex: "case_count", key: "case_count" },
  {
    title: "覆盖率",
    dataIndex: "coverage_rate",
    key: "coverage_rate",
    render: (val: number) => <Progress percent={Math.round(val * 100)} size="small" />,
  },
];

export default function AnalyticsPage() {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div>
        <Title level={4}>测试资产分析仪表盘</Title>
        <Paragraph type="secondary">
          多维度聚合测试资产数据，展示执行趋势、模块覆盖率、缺陷分布和关键指标。
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="总用例" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总执行" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="平均通过率" value={0} suffix="%" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="自动化率" value={0} suffix="%" />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="总缺陷" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="平均耗时" value={0} suffix="ms" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="执行时长" value={0} suffix="h" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="不稳定率" value={0} suffix="%" />
          </Card>
        </Col>
      </Row>

      <Card title="模块覆盖率">
        <Table columns={columns} dataSource={mockModules} rowKey="module" pagination={false} />
      </Card>
    </Space>
  );
}
