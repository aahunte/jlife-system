const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  memberId: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  chineseName: {
    type: String,
    required: true,
    trim: true
  },
  englishName: {
    type: String,
    trim: true
  },
  birthYear: {
    type: Number,
    required: true
  },
  gender: {
    type: String,
    required: true,
    enum: ['男', '女']
  },
  idStatus: {
    type: String,
    required: true,
    enum: ['永久身份證', '單程證', '雙程證']
  },
  economicStatus: {
    type: String,
    required: true,
    enum: ['低收入家庭', '綜援家庭', '無收入家庭', '其他']
  },
  phone: {
    type: String,
    trim: true
  },
  address: {
    type: String,
    required: true,
    trim: true
  },
  residenceType: {
    type: String,
    required: true,
    enum: ['劏房', '公屋']
  },
  maritalStatus: {
    type: String,
    required: true,
    enum: ['單身', '已婚', '離婚/分居']
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

const User = mongoose.model('User', userSchema);

module.exports = User; 