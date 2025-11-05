import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { analysisAPI, industryAPI } from '../services/api'

const Dashboard = () => {
  const [recommendations, setRecommendations] = useState([])
  const [industries, setIndustries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [recRes, indRes] = await Promise.all([
        analysisAPI.getRecommendations({ top_n: 10 }),
        industryAPI.getIndustryRanking()
      ])

      if (recRes.code === 200) {
        setRecommendations(recRes.data)
      }
      if (indRes.code === 200) {
        setIndustries(indRes.data.slice(0, 5))
      }
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code'
    },
    {
      title: '格雷厄姆评分',
      dataIndex: 'graham_score',
      key: 'graham_score',
      render: (score) => <span>{score?.toFixed(2)}</span>
    },
    {
      title: '安全边际',
      dataIndex: 'safety_margin',
      key: 'safety_margin',
      render: (margin) => <span>{margin?.toFixed(2)}%</span>
    },
    {
      title: '推荐级别',
      dataIndex: 'recommendation',
      key: 'recommendation'
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表盘</h1>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="推荐股票数量"
              value={recommendations.length}
              valueStyle={{ color: '#3f8600' }}
              prefix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="热门行业数量"
              value={industries.length}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="分析完成率"
              value={93}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card title="今日推荐股票" style={{ marginBottom: 24 }}>
        <Table
          columns={columns}
          dataSource={recommendations}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 5 }}
        />
      </Card>

      <Card title="热门行业">
        <Table
          columns={[
            { title: '行业名称', dataIndex: 'name', key: 'name' },
            {
              title: '涨跌幅',
              dataIndex: 'price_change',
              key: 'price_change',
              render: (val) => <span style={{ color: val > 0 ? 'red' : 'green' }}>
                {val?.toFixed(2)}%
              </span>
            }
          ]}
          dataSource={industries}
          loading={loading}
          rowKey="code"
          pagination={false}
        />
      </Card>
    </div>
  )
}

export default Dashboard
