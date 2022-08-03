/**
 * (c) 2013 Beau Sorensen
 * MIT Licensed
 * For all details and documentation:
 * https://github.com/sorensen/ascii-table
 */

 ;(function() {
  'use strict';
  
  /*!
   * Module dependencies
   */
  
  var slice = Array.prototype.slice
    , toString = Object.prototype.toString
  
  /**
   * AsciiTable constructor
   *
   * @param {String|Object} title or JSON table
   * @param {Object} table options
   *  - `prefix` - string prefix added to each line on render
   * @constructor
   * @api public
   */
  
  function AsciiTable(name, options) {
    this.options = options || {}
    this.reset(name)
  }
  
  /*!
   * Alignment constants
   */
  
  AsciiTable.LEFT = 0
  AsciiTable.CENTER = 1
  AsciiTable.RIGHT = 2
  
  /*!
   * Static methods
   */
  
  /**
   * Create a new table instance
   *
   * @param {String|Object} title or JSON table
   * @param {Object} table options
   * @api public
   */
  
  AsciiTable.factory = function(name, options) {
    return new AsciiTable(name, options)
  }
  
  /**
   * Align the a string at the given length
   *
   * @param {Number} direction
   * @param {String} string input
   * @param {Number} string length
   * @param {Number} padding character
   * @api public
   */
  
  AsciiTable.align = function(dir, str, len, pad) {
    if (dir === AsciiTable.LEFT) return AsciiTable.alignLeft(str, len, pad)
    if (dir === AsciiTable.RIGHT) return AsciiTable.alignRight(str, len, pad)
    if (dir === AsciiTable.CENTER) return AsciiTable.alignCenter(str, len, pad)
    return AsciiTable.alignAuto(str, len, pad)
  }
  
  /**
   * Left align a string by padding it at a given length
   *
   * @param {String} str
   * @param {Number} string length
   * @param {String} padding character (optional, default '')
   * @api public
   */
  
  AsciiTable.alignLeft = function(str, len, pad) {
    var strlen = null
    if (!len || len < 0) return ''
    if (str === undefined || str === null) str = ''
    if (typeof pad === 'undefined') pad = ' '
    // If we want to display an HTML element then we want to
    // consider the length of the innerText.
    if (str instanceof Element) {
      strlen = str.innerText.length;
      str = str.outerHTML;
    }
    else if (typeof str !== 'string') str = str.toString()
    else if (str.startsWith('<a') && str.endsWith('</a>')) {
      strlen = str.length
      let startIndex = str.indexOf('<a');
      new_str = str.substring(0, startIndex);
      while (startIndex != -1) {
        const endIndex = str.indexOf('>', startIndex+1);
        strlen -= (endIndex-startIndex+5);
        startIndex = str.indexOf('<a', endIndex+1);
        new_str += str.substring(endIndex+1, startIndex);
      }

      new_str += str.substring(startIndex+1)
      str = new_str
      // str = str.substring(innerIndex+1, outerIndex)
    }
    if (!strlen) strlen = str.length;
    var alen = len + 1 - strlen
    if (alen <= 0) return str
    return str + Array(len + 1 - strlen).join(pad)
  }
  
  /**
   * Center align a string by padding it at a given length
   *
   * @param {String} str
   * @param {Number} string length
   * @param {String} padding character (optional, default '')
   * @api public
   */
  
  AsciiTable.alignCenter = function(str, len, pad) {
    var strlen = null
    if (!len || len < 0) return ''
    if (str === undefined || str === null) str = ''
    if (typeof pad === 'undefined') pad = ' '
    // If we want to display an HTML element then we want to
    // consider the length of the innerText.
    if (str instanceof Element) {
      strlen = str.innerText.length;
      str = str.outerHTML;
    }
    else if (typeof str !== 'string') str = str.toString()
    else if (str.startsWith('<a') && str.endsWith('</a>')) {
      strlen = str.length
      let startIndex = str.indexOf('<a');
      new_str = str.substring(0, startIndex);
      while (startIndex != -1) {
        const endIndex = str.indexOf('>', startIndex+1);
        strlen -= (endIndex-startIndex+5);
        startIndex = str.indexOf('<a', endIndex+1);
        new_str += str.substring(endIndex+1, startIndex);
      }

      new_str += str.substring(startIndex+1)
      str = new_str
      // str = str.substring(innerIndex+1, outerIndex)
    }
    if (!strlen) strlen = str.length;
    var nLen = strlen
      , half = Math.floor(len / 2 - nLen / 2)
      , odds = Math.abs((nLen % 2) - (len % 2))
      , len = strlen

    return AsciiTable.alignRight('', half, pad) 
      + str
      + AsciiTable.alignLeft('', half + odds, pad)
  }
  
  /**
   * Right align a string by padding it at a given length
   *
   * @param {String} str
   * @param {Number} string length
   * @param {String} padding character (optional, default '')
   * @api public
   */
  
  AsciiTable.alignRight = function(str, len, pad) {
    var strlen = null
    if (!len || len < 0) return ''
    if (str === undefined || str === null) str = ''
    if (typeof pad === 'undefined') pad = ' '
    // If we want to display an HTML element then we want to
    // consider the length of the innerText.
    if (str instanceof Element) {
      strlen = str.innerText.length;
      str = str.outerHTML;
    }
    else if (typeof str !== 'string') str = str.toString()
    else if (str.startsWith('<a') && str.endsWith('</a>')) {
      strlen = str.length
      let startIndex = str.indexOf('<a');
      new_str = str.substring(0, startIndex);
      while (startIndex != -1) {
        const endIndex = str.indexOf('>', startIndex+1);
        strlen -= (endIndex-startIndex+5);
        startIndex = str.indexOf('<a', endIndex+1);
        new_str += str.substring(endIndex+1, startIndex);
      }

      new_str += str.substring(startIndex+1)
      str = new_str
      // str = str.substring(innerIndex+1, outerIndex)
    }
    if (!strlen) strlen = str.length;
    var alen = len + 1 - strlen

    if (alen <= 0) return str
    return Array(len + 1 - strlen).join(pad) + str
  }
  
  /**
   * Auto align string value based on object type
   *
   * @param {Any} object to string
   * @param {Number} string length
   * @param {String} padding character (optional, default '')
   * @api public
   */
  
  AsciiTable.alignAuto = function(str, len, pad) {
    var strlen = 0;
    if (str === undefined || str === null) str = ''
    var type = toString.call(str)
    pad || (pad = ' ')
    len = +len
    // If we want to display an HTML element then we want to
    // consider the length of the innerText.
    if (str instanceof Element) strlen = str.innerText.length
    else if (typeof str !== 'string') str = str.toString()
    else if (str.startsWith('<a') && str.endsWith('</a>')) {
      strlen = str.length
      let startIndex = str.indexOf('<a');
      new_str = str.substring(0, startIndex);
      while (startIndex != -1) {
        const endIndex = str.indexOf('>', startIndex+1);
        strlen -= (endIndex-startIndex+5);
        startIndex = str.indexOf('<a', endIndex+1);
        new_str += str.substring(endIndex+1, startIndex);
      }

      new_str += str.substring(startIndex+1)
      str = new_str
      // str = str.substring(innerIndex+1, outerIndex)
    }
    if (!strlen) strlen = str.length;
    if (strlen < len) {
      switch(type) {
        case '[object Number]': return AsciiTable.alignRight(str, len, pad)
        default: return AsciiTable.alignLeft(str, len, pad)
      }
    }
    if (str instanceof Element) return str.outerHTML
    return str
  }
  
  /**
   * Fill an array at a given size with the given value
   *
   * @param {Number} array size
   * @param {Any} fill value
   * @return {Array} filled array
   * @api public
   */
  
  AsciiTable.arrayFill = function(len, fill) {
    var arr = new Array(len)
    for (var i = 0; i !== len; i++) {
      arr[i] = fill;
    }
    return arr
  }
  
  /*!
   * Instance methods
   */
  
  /**
   * Reset the table state back to defaults
   *
   * @param {String|Object} title or JSON table
   * @api public
   */
  
  AsciiTable.prototype.reset = 
  AsciiTable.prototype.clear = function(name) {
    this.__name = ''
    this.__nameAlign = AsciiTable.CENTER
    this.__rows = []
    this.__maxCells = 0
    this.__aligns = []
    this.__colMaxes = []
    this.__spacing = 1
    this.__heading = null
    this.__headingAlign = AsciiTable.CENTER
    this.setBorder()
  
    if (toString.call(name) === '[object String]') {
      this.__name = name
    } else if (toString.call(name) === '[object Object]') {
      this.fromJSON(name)
    } else if (name instanceof Element) {
      this.__name = name
    }
    return this
  }
  
  /**
   * Set the table border
   *
   * @param {String} horizontal edges (optional, default `|`)
   * @param {String} vertical edges (optional, default `-`)
   * @param {String} top corners (optional, default `.`)
   * @param {String} bottom corners (optional, default `'`)
   * @api public
   */
  
  AsciiTable.prototype.setBorder = function(edge, fill, top, bottom) {
    this.__border = true
    if (arguments.length === 1) {
      fill = top = bottom = edge
    }
    this.__edge = edge || '|'
    this.__fill = fill || '-'
    this.__top = top || '.'
    this.__bottom = bottom || "'"
    return this
  }
  
  /**
   * Remove all table borders
   *
   * @api public
   */
  
  AsciiTable.prototype.removeBorder = function() {
    this.__border = false
    this.__edge = ' '
    this.__fill = ' '
    return this
  }
  
  /**
   * Set the column alignment at a given index
   *
   * @param {Number} column index
   * @param {Number} alignment direction
   * @api public
   */
  
  AsciiTable.prototype.setAlign = function(idx, dir) {
    this.__aligns[idx] = dir
    return this
  }
  
  /**
   * Set the title of the table
   *
   * @param {String} title
   * @api public
   */
  
  AsciiTable.prototype.setTitle = function(name) {
    this.__name = name
    return this
  }
  
  /**
   * Get the title of the table
   *
   * @return {String} title
   * @api public
   */
  
  AsciiTable.prototype.getTitle = function() {
    return this.__name
  }
  
  /**
   * Set table title alignment
   *
   * @param {Number} direction
   * @api public
   */
  
  AsciiTable.prototype.setTitleAlign = function(dir) {
    this.__nameAlign = dir
    return this
  }
  
  /**
   * AsciiTable sorting shortcut to sort rows
   *
   * @param {Function} sorting method
   * @api public
   */
  
  AsciiTable.prototype.sort = function(method) {
    this.__rows.sort(method)
    return this
  }
  
  /**
   * Sort rows based on sort method for given column
   *
   * @param {Number} column index
   * @param {Function} sorting method
   * @api public
   */
  
  AsciiTable.prototype.sortColumn = function(idx, method) {
    this.__rows.sort(function(a, b) {
      return method(a[idx], b[idx])
    })
    return this
  }
  
  /**
   * Set table heading for columns
   *
   * @api public
   */
  
  AsciiTable.prototype.setHeading = function(row) {
    if (arguments.length > 1 || toString.call(row) !== '[object Array]') {
      row = slice.call(arguments)
    }
    this.__heading = row
    return this
  }
  
  /**
   * Get table heading for columns
   *
   * @return {Array} copy of headings
   * @api public
   */
  
  AsciiTable.prototype.getHeading = function() {
    return this.__heading.slice()
  }
  
  /**
   * Set heading alignment
   *
   * @param {Number} direction
   * @api public
   */
  
  AsciiTable.prototype.setHeadingAlign = function(dir) {
    this.__headingAlign = dir
    return this
  }
  
  /**
   * Add a row of information to the table
   * 
   * @param {...|Array} argument values in order of columns
   * @api public
   */
  
  AsciiTable.prototype.addRow = function(row) {
    if (arguments.length > 1 || toString.call(row) !== '[object Array]') {
      row = slice.call(arguments)
    }
    this.__maxCells = Math.max(this.__maxCells, row.length)
    this.__rows.push(row)
    return this
  }
  
  /**
   * Get a copy of all rows of the table
   *
   * @return {Array} copy of rows
   * @api public
   */
  
  AsciiTable.prototype.getRows = function() {
    return this.__rows.slice().map(function(row) {
      return row.slice()
    })
  }
  
  /**
   * Add rows in the format of a row matrix
   *
   * @param {Array} row matrix
   * @api public
   */
  
  AsciiTable.prototype.addRowMatrix = function(rows) {
    for (var i = 0; i < rows.length; i++) {
      this.addRow(rows[i])
    }
    return this
  }
  
  /**
   * Add rows from the given data array, processed by the callback function rowCallback.
   *
   * @param {Array} data
   * @param (Function) rowCallback
   * @param (Boolean) asMatrix - controls if the row created by rowCallback should be assigned as row matrix
   * @api public
   */
  
  AsciiTable.prototype.addData = function(data, rowCallback, asMatrix) {
    if (toString.call(data) !== '[object Array]') {
      return this;
    }
    for (var index = 0, limit = data.length; index < limit; index++) {
      var row = rowCallback(data[index]);
      if(asMatrix) {
        this.addRowMatrix(row);
      } else {
        this.addRow(row);
      }
    }
    return this
  }
  
    /**
   * Reset the current row state
   *
   * @api public
   */
  
  AsciiTable.prototype.clearRows = function() {
    this.__rows = []
    this.__maxCells = 0
    this.__colMaxes = []
    return this
  }
  
  /**
   * Apply an even spaced column justification
   *
   * @param {Boolean} on / off
   * @api public
   */
  
  AsciiTable.prototype.setJustify = function(val) {
    arguments.length === 0 && (val = true)
    this.__justify = !!val
    return this
  }
  
  /**
   * Convert the current instance to a JSON structure
   *
   * @return {Object} json representation
   * @api public
   */
  
  AsciiTable.prototype.toJSON = function() {
    return {
      title: this.getTitle()
    , heading: this.getHeading()
    , rows: this.getRows()
    }
  }
  
  /**
   * Populate the table from a JSON object
   *
   * @param {Object} json representation
   * @api public
   */
  
  AsciiTable.prototype.parse = 
  AsciiTable.prototype.fromJSON = function(obj) {
    return this
      .clear()
      .setTitle(obj.title)
      .setHeading(obj.heading)
      .addRowMatrix(obj.rows)
  }
  
  /**
   * Render the table with the current information
   *
   * @return {String} formatted table
   * @api public
   */
  
  AsciiTable.prototype.render =
  AsciiTable.prototype.valueOf =
  AsciiTable.prototype.toString = function() {
    var self = this
      , body = []
      , mLen = this.__maxCells
      , max = AsciiTable.arrayFill(mLen, 0)
      , total = mLen * 3
      , rows = this.__rows
      , justify
      , border = this.__border
      , all = this.__heading 
          ? [this.__heading].concat(rows)
          : rows
  
    // Calculate max table cell lengths across all rows
    for (var i = 0; i < all.length; i++) {
      var row = all[i]
      for (var k = 0; k < mLen; k++) {
        var cell = row[k]
        var strlen = cell ? cell.toString().length : 0;
        // If we want to display an HTML element then we want to
        // consider the length of the innerText.
        if (cell instanceof Element) strlen = cell.innerText.length;
        else if (cell && cell.toString().includes('<a') && cell.toString().includes('</a>')) {
          const str = cell.toString()
          strlen = str.length
          let startIndex = str.indexOf('<a');
          while (startIndex != -1) {
            const endIndex = str.indexOf('>', startIndex+1);
            strlen -= (endIndex-startIndex+5);
            startIndex = str.indexOf('<a', endIndex+1);
          }
        }
        max[k] = Math.max(max[k], cell ? strlen : 0)
      }
    }
    this.__colMaxes = max
    justify = this.__justify ? Math.max.apply(null, max) : 0
  
    // Get 
    max.forEach(function(x) {
      total += justify ? justify : x + self.__spacing
    })
    justify && (total += max.length)
    total -= this.__spacing
  
    // Heading
    border && body.push(this._seperator(total - mLen + 1, this.__top))
    if (this.__name) {
      body.push(this._renderTitle(total - mLen + 1))
      border && body.push(this._seperator(total - mLen + 1))
    }
    if (this.__heading) {
      body.push(this._renderRow(this.__heading, ' ', this.__headingAlign))
      body.push(this._rowSeperator(mLen, this.__fill))
    }
    for (var i = 0; i < this.__rows.length; i++) {
      body.push(this._renderRow(this.__rows[i], ' '))
    }
    border && body.push(this._seperator(total - mLen + 1, this.__bottom))
  
    var prefix = this.options.prefix || ''
    return prefix + body.join('\n' + prefix)
  }
  
  /**
   * Create a line seperator
   *
   * @param {Number} string size
   * @param {String} side values (default '|')
   * @api private
   */
  
  AsciiTable.prototype._seperator = function(len, sep) {
    sep || (sep = this.__edge)
    return sep + AsciiTable.alignRight(sep, len, this.__fill)
  }
  
  /**
   * Create a row seperator
   *
   * @return {String} seperator
   * @api private
   */
  
  AsciiTable.prototype._rowSeperator = function() {
    var blanks = AsciiTable.arrayFill(this.__maxCells, this.__fill)
    return this._renderRow(blanks, this.__fill)
  }
  
  /**
   * Render the table title in a centered box
   *
   * @param {Number} string size
   * @return {String} formatted title
   * @api private
   */
  
  AsciiTable.prototype._renderTitle = function(len) {
    var name = this.__name instanceof Element ? this.__name : ' ' + this.__name + ' '
    var str = AsciiTable.align(this.__nameAlign, name, len - 1, ' ')
    return this.__edge + str + this.__edge
  }
  
  /**
   * Render an invdividual row
   *
   * @param {Array} row
   * @param {String} column seperator
   * @param {Number} total row alignment (optional, default `auto`)
   * @return {String} formatted row
   * @api private
   */
  
  AsciiTable.prototype._renderRow = function(row, str, align) {
    var tmp = ['']
      , max = this.__colMaxes
  
    for (var k = 0; k < this.__maxCells; k++) {
      var cell = row[k]
        , just = this.__justify ? Math.max.apply(null, max) : max[k]
        // , pad = k === this.__maxCells - 1 ? just : just + this.__spacing
        , pad = just
        , cAlign = this.__aligns[k]
        , use = align
        , method = 'alignAuto'
    
      if (typeof align === 'undefined') use = cAlign
  
      if (use === AsciiTable.LEFT) method = 'alignLeft'
      if (use === AsciiTable.CENTER) method = 'alignCenter'
      if (use === AsciiTable.RIGHT) method = 'alignRight'
      tmp.push(AsciiTable[method](cell, pad, str))
    }
    var front = tmp.join(str + this.__edge + str)
    front = front.substr(1, front.length)
    return front + str + this.__edge
  }
  
  /*!
   * Aliases
   */
  
  // Create method shortcuts to all alignment methods for each direction
  ;['Left', 'Right', 'Center'].forEach(function(dir) {
    var constant = AsciiTable[dir.toUpperCase()]
  
    ;['setAlign', 'setTitleAlign', 'setHeadingAlign'].forEach(function(method) {
      // Call the base method with the direction constant as the last argument
      AsciiTable.prototype[method + dir] = function() {
        var args = slice.call(arguments).concat(constant)
        return this[method].apply(this, args)
      }
    })
  })
  
  /*!
   * Module exports.
   */
  
  if (typeof exports !== 'undefined') {
    module.exports = AsciiTable
  } else {
    this.AsciiTable = AsciiTable
  }
  
  }).call(this);