odoo.define('sirh_base.ListRenderer', function (require) {
    "use strict";
    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        /**
         * Render the row that represent a group
         *
         * @private
         * @param {Object} group
         * @param {integer} groupLevel the nesting level (0 for root groups)
         * @returns {jQueryElement} a <tr> element
         */
        _renderGroupRow: function (group, groupLevel) {
            var cells = [];

            var name = group.value === undefined ? _t('Undefined') : group.value;
            var groupBy = this.state.groupedBy[groupLevel];

            // Remove integer in the verification of undefined value
            if (['boolean', 'integer'].indexOf(group.fields[groupBy.split(':')[0]].type) == 0) {
                name = name || _t('Undefined');
            }
            var $th = $('<th>')
                .addClass('o_group_name')
                .attr('tabindex', -1)
                .text(name + ' (' + group.count + ')');
            var $arrow = $('<span>')
                .css('padding-left', (groupLevel * 20) + 'px')
                .css('padding-right', '5px')
                .addClass('fa');
            if (group.count > 0) {
                $arrow.toggleClass('fa-caret-right', !group.isOpen)
                    .toggleClass('fa-caret-down', group.isOpen);
            }
            $th.prepend($arrow);
            cells.push($th);

            var aggregateKeys = Object.keys(group.aggregateValues);
            var aggregateValues = _.mapObject(group.aggregateValues, function (value) {
                return {value: value};
            });
            var aggregateCells = this._renderAggregateCells(aggregateValues);
            var firstAggregateIndex = _.findIndex(this.columns, function (column) {
                return column.tag === 'field' && _.contains(aggregateKeys, column.attrs.name);
            });
            var colspanBeforeAggregate;
            if (firstAggregateIndex !== -1) {
                // if there are aggregates, the first $th goes until the first
                // aggregate then all cells between aggregates are rendered
                colspanBeforeAggregate = firstAggregateIndex;
                var lastAggregateIndex = _.findLastIndex(this.columns, function (column) {
                    return column.tag === 'field' && _.contains(aggregateKeys, column.attrs.name);
                });
                cells = cells.concat(aggregateCells.slice(firstAggregateIndex, lastAggregateIndex + 1));
                var colSpan = this.columns.length - 1 - lastAggregateIndex;
                if (colSpan > 0) {
                    cells.push($('<th>').attr('colspan', colSpan));
                }
            } else {
                var colN = this.columns.length;
                colspanBeforeAggregate = colN > 1 ? colN - 1 : 1;
                if (colN > 1) {
                    cells.push($('<th>'));
                }
            }
            if (this.hasSelectors) {
                colspanBeforeAggregate += 1;
            }
            $th.attr('colspan', colspanBeforeAggregate);

            if (group.isOpen && !group.groupedBy.length && (group.count > group.data.length)) {
                var $pager = this._renderGroupPager(group);
                var $lastCell = cells[cells.length - 1];
                $lastCell.append($pager);
            }
            if (group.isOpen && this.groupbys[groupBy]) {
                var $buttons = this._renderGroupButtons(group, this.groupbys[groupBy]);
                if ($buttons.length) {
                    var $buttonSection = $('<div>', {
                        class: 'o_group_buttons',
                    }).append($buttons);
                    $th.append($buttonSection);
                }
            }
            return $('<tr>')
                .addClass('o_group_header')
                .toggleClass('o_group_open', group.isOpen)
                .toggleClass('o_group_has_content', group.count > 0)
                .data('group', group)
                .append(cells);
        },
    });
});