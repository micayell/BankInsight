const bankFileNameMap = new Map([
  ['default', 'IBK.jpg'],
  ['부산은행', 'Busan.jpg'],
  ['대구은행', 'Daegu.jpg'],
  ['광주은행', 'Gwangju.jpg'],
  ['하나은행', 'Hana.jpg'],
  ['중소기업은행', 'IBK.jpg'],
  ['기업은행', 'IBK.jpg'],
  ['제주은행', 'Jeju.jpg'],
  ['전북은행', 'Jeonbuk.jpg'],
  ['주식회사 카카오뱅크', 'Kakao.jpg'],
  ['카카오뱅크', 'Kakao.jpg'],
  ['주식회사 케이뱅크', 'Kbank.png'],
  ['케이뱅크', 'Kbank.png'],
  ['KDB산업은행', 'KDB.jpg'],
  ['한국산업은행', 'KDB.jpg'],
  ['국민은행', 'Kookmin.jpg'],
  ['KB국민은행', 'Kookmin.jpg'],
  ['경남은행', 'Kyungnam.jpg'],
  ['농협은행주식회사', 'Nonghyup.jpg'],
  ['농협은행', 'Nonghyup.jpg'],
  ['신한은행', 'Shinhan.jpg'],
  ['SC제일은행', 'StandardChartered.jpg'],
  ['한국스탠다드차타드은행', 'StandardChartered.jpg'],
  ['수협은행', 'Suhyup.jpg'],
  ['Sh수협은행', 'Suhyup.jpg'],
  ['토스뱅크 주식회사', 'Toss.jpg'],
  ['토스뱅크', 'Toss.jpg'],
  ['우리은행', 'Woori.jpg'],
  ['아이엠뱅크', 'IM.png']
]);

export function getBankLogoUrl(korCoNm) {
  const fileName = bankFileNameMap.get(korCoNm) || bankFileNameMap.get('default');
  return `/bank/${fileName}`;
}
