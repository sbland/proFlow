import { IEdge } from "./edges";

export function sortLinks(lks: IEdge[]) {
  lks.sort(function (a, b) {
    if (a.source > b.source) {
      return 1;
    } else if (a.source < b.source) {
      return -1;
    } else {
      if (a.target > b.target) {
        return 1;
      }
      if (a.target < b.target) {
        return -1;
      } else {
        return 0;
      }
    }
  });
}

export function setLinkIndexAndNum(linksData: IEdge[]) {
  //any links with duplicate source and target get an incremented 'linknum'
  var mLinkNum: { [k: string]: number } = {};
  for (var i = 0; i < linksData.length; i++) {
    if (
      i != 0 &&
      linksData[i].source == linksData[i - 1].source &&
      linksData[i].target == linksData[i - 1].target
    ) {
      linksData[i].linkindex = linksData[i - 1].linkindex + 1;
    } else {
      linksData[i].linkindex = 1;
    }
    // save the total number of links between two nodes
    if (
      mLinkNum[linksData[i].target + "," + linksData[i].source] !== undefined
    ) {
      mLinkNum[linksData[i].target + "," + linksData[i].source] =
        linksData[i].linkindex;
    } else {
      mLinkNum[linksData[i].source + "," + linksData[i].target] =
        linksData[i].linkindex;
    }
  }
  return mLinkNum;
}

// Deprecated ?
// export var getSiblingLinks = function (
//   mLinkNum: { [k: string]: number },
//   source: string,
//   target: string
// ) {
//   var siblings = [];
//   for (var i = 0; i < mLinkNum.length; ++i) {
//     if (
//       (mLinkNum[i].source == source && mLinkNum[i].target == target) ||
//       (mLinkNum[i].source == target && mLinkNum[i].target == source)
//     )
//       siblings.push(mLinkNum[i].id);
//   }
//   return siblings;
// };
