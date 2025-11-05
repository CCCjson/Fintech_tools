import React, { useState, useEffect } from 'react'
import { Table, Card, Tag } from 'antd'
import { analysisAPI } from '../services/api'

const Recommendation = () => {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    setLoading(true)
    try {
      const response = await analysisAPI.getRecommendations({ top_n: 50 })
      if (response.code === 200) {
        setRecommendations(response.data)
      }
    } catch (error) {
      console.error('加载推荐列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case '强烈推荐':
        return 'red'
      case '推荐':
        return 'orange'
      case '可考虑':
        return 'blue'
      default:
        return 'gray'
    }
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case '低':
        return 'green'
      case '中':
        return 'orange'
      case '高':
        return 'red'
      default:
        return 'gray'
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
      render: (score) => <span>{score?.toFixed(2)}</span>,
      sorter: (a, b) => a.graham_score - b.graham_score,
      defaultSortOrder: 'descend'
    },
    {
      title: '内在价值',
      dataIndex: 'intrinsic_value',
      key: 'intrinsic_value',
      render: (val) => `¥${val?.toFixed(2)}`
    },
    {
      title: '当前价格',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (val) => `¥${val?.toFixed(2)}`
    },
    {
      title: '安全边际',
      dataIndex: 'safety_margin',
      key: 'safety_margin',
      render: (margin) => <span>{margin?.toFixed(2)}%</span>,
      sorter: (a, b) => a.safety_margin - b.safety_margin
    },
    {
      title: '推荐级别',
      dataIndex: 'recommendation',
      key: 'recommendation',
      render: (rec) => <Tag color={getRecommendationColor(rec)}>{rec}</Tag>
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (risk) => <Tag color={getRiskColor(risk)}>{risk}</Tag>
    },
    {
      title: '分析日期',
      dataIndex: 'analysis_date',
      key: 'analysis_date'
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>推荐股票列表</h1>

      <Card>
        <Table
          columns={columns}
          dataSource={recommendations}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  )
}

export default Recommendation
