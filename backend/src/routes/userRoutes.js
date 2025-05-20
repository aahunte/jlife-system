const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const auth = require('../middleware/auth');

// 生成会员编号
const generateMemberId = async () => {
  const date = new Date();
  const year = date.getFullYear().toString().slice(-2);
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  
  // 获取当前月份的最大会员编号
  const prefix = `M${year}${month}`;
  const lastMember = await User.findOne({
    memberId: new RegExp(`^${prefix}`)
  }).sort({ memberId: -1 });

  if (!lastMember) {
    return `${prefix}001`;
  }

  const lastNumber = parseInt(lastMember.memberId.slice(-3));
  const newNumber = (lastNumber + 1).toString().padStart(3, '0');
  return `${prefix}${newNumber}`;
};

// 会员注册
router.post('/register', async (req, res) => {
  try {
    const {
      chineseName,
      englishName,
      birthYear,
      gender,
      idStatus,
      economicStatus,
      phone,
      address,
      residenceType,
      maritalStatus
    } = req.body;

    // 检查是否已存在相同中文姓名的会员
    const existingMember = await User.findOne({ chineseName });
    if (existingMember) {
      return res.status(409).json({
        message: '該會員已經存在'
      });
    }

    // 生成会员编号
    const memberId = await generateMemberId();

    // 创建新会员
    const newMember = new User({
      memberId,
      chineseName,
      englishName,
      birthYear,
      gender,
      idStatus,
      economicStatus,
      phone,
      address,
      residenceType,
      maritalStatus
    });

    await newMember.save();

    res.status(201).json({
      message: '會員註冊成功',
      memberId: newMember.memberId
    });
  } catch (error) {
    console.error('會員註冊錯誤:', error);
    res.status(500).json({
      message: '服務器錯誤，請稍後重試'
    });
  }
});

// 获取用户信息（需要认证）
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId);
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }
    res.json(user);
  } catch (error) {
    res.status(500).json({ message: '服务器错误', error: error.message });
  }
});

// 更新用户信息（需要认证）
router.put('/profile', auth, async (req, res) => {
  try {
    const updates = req.body;
    const allowedUpdates = [
      'chineseName',
      'economicStatus',
      'birthYear',
      'gender',
      'idStatus',
      'singlePermitYear',
      'familySize',
      'visitor',
      'district',
      'address',
      'phone',
      'housingEstate',
      'maritalStatus',
      'spouseName',
      'spouseAge',
      'numberOfChildren',
      'spouseOccupation',
      'residenceType',
      'residenceStatus',
      'monthlyRent',
      'familyIncome',
      'hasCSSA'
    ];

    // 过滤不允许更新的字段
    Object.keys(updates).forEach(key => {
      if (!allowedUpdates.includes(key)) {
        delete updates[key];
      }
    });

    const user = await User.findByIdAndUpdate(
      req.user.userId,
      { $set: updates },
      { new: true, runValidators: true }
    );

    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    res.json({
      message: '更新成功',
      user
    });
  } catch (error) {
    res.status(500).json({ message: '服务器错误', error: error.message });
  }
});

// 会员搜索
router.get('/search', async (req, res) => {
  try {
    const { term } = req.query;
    
    if (!term) {
      return res.status(400).json({
        message: '請提供搜索關鍵詞'
      });
    }

    // 搜索会员编号或中文姓名
    const members = await User.find({
      $or: [
        { memberId: { $regex: term, $options: 'i' } },
        { chineseName: { $regex: term, $options: 'i' } }
      ]
    }).select('memberId chineseName englishName gender birthYear idStatus economicStatus');

    res.json(members);
  } catch (error) {
    console.error('會員搜索錯誤:', error);
    res.status(500).json({
      message: '服務器錯誤，請稍後重試'
    });
  }
});

module.exports = router; 